"""Document upload and download routes."""

import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from api.auth import get_current_user
from api.database import get_db
from api.db_models import Case, Document, User
from api.schemas import DocumentInfo

router = APIRouter(tags=["documents"])

_PROJECT_ROOT = Path(__file__).parent.parent.parent
_UPLOADS_DIR = _PROJECT_ROOT / "uploads"
_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
_ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}


@router.post("/api/cases/{case_id}/upload", response_model=list[DocumentInfo])
async def upload_files(
    case_id: str,
    files: list[UploadFile] = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DocumentInfo]:
    """Upload files attached to a case."""
    case = db.query(Case).filter(Case.id == case_id, Case.user_id == user.id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso não encontrado")

    upload_dir = _UPLOADS_DIR / case_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    result: list[DocumentInfo] = []

    for upload_file in files:
        content = await upload_file.read()
        if len(content) > _MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"Arquivo '{upload_file.filename}' excede o limite de 10MB",
            )

        if upload_file.content_type and upload_file.content_type not in _ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Tipo '{upload_file.content_type}' não permitido para '{upload_file.filename}'",
            )

        filename = upload_file.filename or "arquivo"
        file_path = upload_dir / filename
        file_path.write_bytes(content)

        doc = Document(
            case_id=case_id,
            tipo="upload",
            nome_arquivo=filename,
            caminho=str(file_path),
            content_type=upload_file.content_type,
            tamanho=len(content),
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        result.append(DocumentInfo.model_validate(doc))

    return result


@router.get("/api/documents/{doc_id}/download")
def download_document(
    doc_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    """Download a document file."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")

    # Verify user owns the case
    case = db.query(Case).filter(Case.id == doc.case_id, Case.user_id == user.id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")

    file_path = Path(doc.caminho)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado no servidor")

    return FileResponse(
        path=str(file_path),
        filename=doc.nome_arquivo,
        media_type=doc.content_type or "application/octet-stream",
    )
