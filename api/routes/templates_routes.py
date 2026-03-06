"""Template management routes."""

import json
import os
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from api.auth import get_current_user
from api.database import get_db
from api.db_models import Case, CaseTemplate, Template, User
from api.schemas import (
    CaseTemplateResponse,
    CaseTemplateSelectRequest,
    CaseTemplateSuggestionResponse,
    TemplateCreateRequest,
    TemplateListResponse,
    TemplateResponse,
    TemplateUpdateRequest,
)

router = APIRouter(prefix="/api/templates", tags=["templates"])

EDIT_ROLES = {"admin", "manager"}

_PROJECT_ROOT = Path(__file__).parent.parent.parent
TEMPLATES_STORE = _PROJECT_ROOT / "templates_store"


def _ensure_store():
    TEMPLATES_STORE.mkdir(parents=True, exist_ok=True)


def _template_to_response(t: Template) -> TemplateResponse:
    materias = []
    if t.materias_aplicaveis:
        try:
            materias = json.loads(t.materias_aplicaveis)
        except (json.JSONDecodeError, TypeError):
            materias = []
    return TemplateResponse(
        id=t.id,
        nome=t.nome,
        descricao=t.descricao,
        categoria=t.categoria,
        materias_aplicaveis=materias,
        ativo=bool(t.ativo),
        caminho_docx=t.caminho_docx,
        created_at=t.created_at,
    )


@router.get("", response_model=TemplateListResponse)
def list_templates(
    search: str | None = Query(None),
    categoria: str | None = Query(None),
    ativo: bool | None = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TemplateListResponse:
    """List all templates."""
    query = db.query(Template)
    if search:
        like_term = f"%{search}%"
        query = query.filter(
            (Template.nome.ilike(like_term)) | (Template.descricao.ilike(like_term))
        )
    if categoria:
        query = query.filter(Template.categoria == categoria)
    if ativo is not None:
        query = query.filter(Template.ativo == (1 if ativo else 0))

    total = query.count()
    templates = query.order_by(Template.created_at.desc()).all()
    return TemplateListResponse(
        templates=[_template_to_response(t) for t in templates],
        total=total,
    )


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TemplateResponse:
    """Get a single template by ID."""
    t = db.query(Template).filter(Template.id == template_id).first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modelo nao encontrado")
    return _template_to_response(t)


@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    body: TemplateCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TemplateResponse:
    """Create a new template (metadata only, upload DOCX separately)."""
    if user.role not in EDIT_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissao")

    t = Template(
        nome=body.nome,
        descricao=body.descricao,
        categoria=body.categoria,
        materias_aplicaveis=json.dumps(body.materias_aplicaveis, ensure_ascii=False),
        created_by=user.id,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return _template_to_response(t)


@router.patch("/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: str,
    body: TemplateUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TemplateResponse:
    """Update template metadata."""
    if user.role not in EDIT_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissao")

    t = db.query(Template).filter(Template.id == template_id).first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modelo nao encontrado")

    update_data = body.model_dump(exclude_unset=True)
    if "materias_aplicaveis" in update_data:
        update_data["materias_aplicaveis"] = json.dumps(
            update_data["materias_aplicaveis"], ensure_ascii=False
        )
    if "ativo" in update_data:
        update_data["ativo"] = 1 if update_data["ativo"] else 0

    for field, value in update_data.items():
        setattr(t, field, value)

    db.commit()
    db.refresh(t)
    return _template_to_response(t)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a template."""
    if user.role not in EDIT_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissao")

    t = db.query(Template).filter(Template.id == template_id).first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modelo nao encontrado")

    # Remove DOCX file if exists
    if t.caminho_docx and os.path.exists(t.caminho_docx):
        os.remove(t.caminho_docx)

    db.delete(t)
    db.commit()


@router.post("/{template_id}/upload", response_model=TemplateResponse)
def upload_template_docx(
    template_id: str,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TemplateResponse:
    """Upload a DOCX file for a template."""
    if user.role not in EDIT_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissao")

    t = db.query(Template).filter(Template.id == template_id).first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modelo nao encontrado")

    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas arquivos .docx sao aceitos",
        )

    _ensure_store()
    dest = TEMPLATES_STORE / f"{t.id}.docx"
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Remove old file if different path
    if t.caminho_docx and t.caminho_docx != str(dest) and os.path.exists(t.caminho_docx):
        os.remove(t.caminho_docx)

    t.caminho_docx = str(dest)
    db.commit()
    db.refresh(t)
    return _template_to_response(t)


@router.get("/{template_id}/download")
def download_template_docx(
    template_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download the DOCX file for a template."""
    from fastapi.responses import FileResponse

    t = db.query(Template).filter(Template.id == template_id).first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modelo nao encontrado")

    if not t.caminho_docx or not os.path.exists(t.caminho_docx):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo DOCX nao encontrado"
        )

    filename = f"{t.nome.replace(' ', '_')}.docx"
    return FileResponse(
        t.caminho_docx,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
    )


# --- Case-Template endpoints ---

case_templates_router = APIRouter(prefix="/api/cases", tags=["case-templates"])


@case_templates_router.get("/{case_id}/templates/suggestions", response_model=CaseTemplateSuggestionResponse)
def suggest_templates_for_case(
    case_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CaseTemplateSuggestionResponse:
    """Suggest templates based on case materia, briefing, and documents."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case or case.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso nao encontrado")

    # Get already selected template IDs
    existing = db.query(CaseTemplate).filter(CaseTemplate.case_id == case_id).all()
    already_selected = [ct.template_id for ct in existing]

    # Get all active templates
    all_templates = db.query(Template).filter(Template.ativo == 1).all()

    suggested = []
    for t in all_templates:
        score = _calculate_suggestion_score(t, case)
        if score > 0:
            suggested.append((score, t))

    # Sort by score descending
    suggested.sort(key=lambda x: x[0], reverse=True)

    return CaseTemplateSuggestionResponse(
        suggested=[_template_to_response(t) for _, t in suggested],
        already_selected=already_selected,
    )


def _calculate_suggestion_score(template: Template, case: Case) -> int:
    """Calculate how relevant a template is for a given case."""
    score = 0

    # Match by materia
    if template.materias_aplicaveis and case.materia:
        try:
            materias = json.loads(template.materias_aplicaveis)
            if case.materia in materias:
                score += 10
            # "Todos" or empty list means applicable to all
            if not materias:
                score += 5
        except (json.JSONDecodeError, TypeError):
            pass

    # Built-in templates always have base relevance
    if template.categoria in ("procuracao", "contrato"):
        score += 5

    # Match keywords in briefing
    briefing_lower = (case.briefing or "").lower()
    nome_lower = template.nome.lower()
    if any(word in briefing_lower for word in nome_lower.split() if len(word) > 3):
        score += 3

    # Match keywords in descricao against briefing
    if template.descricao:
        desc_words = [w for w in template.descricao.lower().split() if len(w) > 3]
        matches = sum(1 for w in desc_words if w in briefing_lower)
        score += min(matches, 5)

    return score


@case_templates_router.get("/{case_id}/templates", response_model=list[CaseTemplateResponse])
def list_case_templates(
    case_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CaseTemplateResponse]:
    """List templates selected for a case."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case or case.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso nao encontrado")

    cts = (
        db.query(CaseTemplate)
        .filter(CaseTemplate.case_id == case_id)
        .all()
    )

    result = []
    for ct in cts:
        t = db.query(Template).filter(Template.id == ct.template_id).first()
        if t:
            result.append(CaseTemplateResponse(
                id=ct.id,
                template_id=t.id,
                template_nome=t.nome,
                template_categoria=t.categoria,
                template_descricao=t.descricao,
                status=ct.status,
                caminho_gerado=ct.caminho_gerado,
                created_at=ct.created_at,
            ))
    return result


@case_templates_router.post("/{case_id}/templates", response_model=list[CaseTemplateResponse])
def select_case_templates(
    case_id: str,
    body: CaseTemplateSelectRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CaseTemplateResponse]:
    """Select templates for a case (replaces previous selection)."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case or case.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso nao encontrado")

    # Remove existing selections
    db.query(CaseTemplate).filter(CaseTemplate.case_id == case_id).delete()

    # Add new selections
    for tid in body.template_ids:
        t = db.query(Template).filter(Template.id == tid).first()
        if not t:
            continue
        ct = CaseTemplate(case_id=case_id, template_id=tid, status="selected")
        db.add(ct)

    db.commit()

    # Return updated list
    return list_case_templates(case_id, user, db)
