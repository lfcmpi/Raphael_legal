"""Case management routes."""

import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.auth import get_current_user
from api.database import get_db, SessionLocal
from api.db_models import User
from api.schemas import (
    CaseCreateRequest,
    CaseDetail,
    CaseListResponse,
    CaseStatusResponse,
    CaseSummary,
    CaseUpdateRequest,
    DocumentInfo,
)
from api.services import case_service

router = APIRouter(prefix="/api/cases", tags=["cases"])

EDIT_ROLES = {"admin", "manager"}


def _case_to_summary(case) -> CaseSummary:
    return CaseSummary.model_validate(case)


def _case_to_detail(case) -> CaseDetail:
    ficha_json = None
    if case.ficha_json:
        try:
            ficha_json = json.loads(case.ficha_json)
        except (json.JSONDecodeError, TypeError):
            ficha_json = None

    docs = [DocumentInfo.model_validate(d) for d in case.documents]

    return CaseDetail(
        id=case.id,
        caso_id=case.caso_id,
        status=case.status,
        materia=case.materia,
        complexidade=case.complexidade,
        cliente_nome=case.cliente_nome,
        resumo=case.resumo,
        alerta_complexo=case.alerta_complexo,
        created_at=case.created_at,
        processed_at=case.processed_at,
        briefing=case.briefing,
        ficha_json=ficha_json,
        panorama_md=case.panorama_md,
        output_completo_md=case.output_completo_md,
        documentos=docs,
    )


def _bg_process(case_id: str) -> None:
    """Run case processing in a background thread with its own DB session."""
    db = SessionLocal()
    try:
        case_service.process_case(db, case_id)
    finally:
        db.close()


@router.get("", response_model=CaseListResponse)
def list_cases(
    materia: str | None = Query(None),
    complexidade: str | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CaseListResponse:
    """List all cases for the current user with optional filters."""
    cases, total = case_service.list_cases(
        db, user.id, materia=materia, complexidade=complexidade, search=search, page=page, per_page=per_page
    )
    return CaseListResponse(
        cases=[_case_to_summary(c) for c in cases],
        total=total,
    )


@router.get("/{case_id}", response_model=CaseDetail)
def get_case(
    case_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CaseDetail:
    """Get detailed case information."""
    case = case_service.get_case(db, case_id)
    if not case or case.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso nao encontrado")
    return _case_to_detail(case)


@router.post("", response_model=CaseSummary, status_code=status.HTTP_201_CREATED)
def create_case(
    body: CaseCreateRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CaseSummary:
    """Create a new case and start processing in background."""
    case = case_service.create_case(db, body.briefing, user.id)
    background_tasks.add_task(_bg_process, case.id)
    return _case_to_summary(case)


@router.patch("/{case_id}", response_model=CaseDetail)
def update_case(
    case_id: str,
    body: CaseUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CaseDetail:
    """Update case fields. Requires admin or manager role."""
    if user.role not in EDIT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissao para editar casos",
        )

    case = case_service.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso nao encontrado")

    update_data = body.model_dump(exclude_unset=True)

    # Handle ficha_json separately — store as JSON string
    if "ficha_json" in update_data:
        ficha = update_data.pop("ficha_json")
        if ficha is not None:
            case.ficha_json = json.dumps(ficha, ensure_ascii=False)
        else:
            case.ficha_json = None

    for field, value in update_data.items():
        setattr(case, field, value)

    db.commit()
    db.refresh(case)
    return _case_to_detail(case)


@router.post("/{case_id}/process", response_model=CaseStatusResponse)
def reprocess_case(
    case_id: str,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CaseStatusResponse:
    """Re-process a case (e.g. after an error or to refresh with updated AI)."""
    from api.db_models import Document

    case = case_service.get_case(db, case_id)
    if not case or case.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso nao encontrado")

    # Remove generated documents (keep uploads)
    db.query(Document).filter(
        Document.case_id == case_id,
        Document.tipo.in_(["procuracao", "contrato_honorarios", "panorama", "ficha"]),
    ).delete(synchronize_session=False)

    case.status = "pending"
    case.error_message = None
    db.commit()

    background_tasks.add_task(_bg_process, case.id)
    return CaseStatusResponse(status="processing", progress="Iniciando processamento...")


@router.get("/{case_id}/status", response_model=CaseStatusResponse)
def case_status(
    case_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CaseStatusResponse:
    """Get current processing status of a case."""
    case = case_service.get_case(db, case_id)
    if not case or case.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso nao encontrado")

    progress_map = {
        "pending": "Aguardando processamento...",
        "processing": "Processando com Claude AI...",
        "completed": "Processamento concluido!",
        "error": f"Erro: {case.error_message or 'desconhecido'}",
    }
    return CaseStatusResponse(
        status=case.status,
        progress=progress_map.get(case.status, case.status),
    )
