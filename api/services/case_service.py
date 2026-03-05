"""Case processing service — orchestrates CaseProcessor + DB + DocumentGenerator."""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from api.db_models import Case, Document
from raphael_legal.config import Settings
from raphael_legal.document_generator import DocumentGenerator
from raphael_legal.processor import CaseProcessor

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent.parent


def create_case(db: Session, briefing: str, user_id: str) -> Case:
    """Create a new case in the database with status='pending'."""
    case = Case(
        briefing=briefing,
        user_id=user_id,
        status="pending",
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def process_case(db: Session, case_id: str) -> None:
    """Process a case using CaseProcessor, save results to DB and generate DOCX files."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        logger.error("Caso não encontrado: %s", case_id)
        return

    case.status = "processing"
    db.commit()

    try:
        settings = Settings()
        processor = CaseProcessor(api_key=settings.ANTHROPIC_API_KEY)
        result = processor.process(case.briefing)

        ficha = result.ficha
        case.caso_id = ficha.caso_id
        case.materia = ficha.materia.value if ficha.materia else None
        case.complexidade = ficha.complexidade.value if ficha.complexidade else None
        case.cliente_nome = ficha.cliente.nome if ficha.cliente else None
        case.resumo = ficha.resumo
        case.ficha_json = ficha.model_dump_json()
        case.panorama_md = result.panorama_md
        case.output_completo_md = result.output_completo_md
        case.alerta_complexo = ficha.alerta_complexo
        case.status = "completed"
        case.processed_at = datetime.now(timezone.utc)

        # Generate DOCX documents
        output_dir = settings.OUTPUT_DIR / ficha.caso_id
        doc_generator = DocumentGenerator(settings.TEMPLATES_DIR)
        generated_files = doc_generator.generate(result, output_dir)

        for file_path in generated_files:
            doc = Document(
                case_id=case.id,
                tipo=file_path.stem,  # "procuracao" or "contrato_honorarios"
                nome_arquivo=file_path.name,
                caminho=str(file_path),
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                tamanho=file_path.stat().st_size,
            )
            db.add(doc)

        # Save panorama and ficha as files too
        panorama_path = output_dir / "panorama.md"
        panorama_path.write_text(result.panorama_md, encoding="utf-8")
        db.add(Document(
            case_id=case.id,
            tipo="panorama",
            nome_arquivo="panorama.md",
            caminho=str(panorama_path),
            content_type="text/markdown",
            tamanho=panorama_path.stat().st_size,
        ))

        ficha_path = output_dir / "ficha.json"
        ficha_path.write_text(ficha.model_dump_json(indent=2), encoding="utf-8")
        db.add(Document(
            case_id=case.id,
            tipo="ficha",
            nome_arquivo="ficha.json",
            caminho=str(ficha_path),
            content_type="application/json",
            tamanho=ficha_path.stat().st_size,
        ))

        db.commit()

    except Exception as e:
        logger.exception("Erro ao processar caso %s", case_id)
        case.status = "error"
        case.error_message = str(e)
        db.commit()


def get_case(db: Session, case_id: str) -> Case | None:
    """Get a case by ID."""
    return db.query(Case).filter(Case.id == case_id).first()


def list_cases(
    db: Session,
    user_id: str,
    materia: str | None = None,
    complexidade: str | None = None,
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Case], int]:
    """List cases with optional filters and pagination."""
    query = db.query(Case).filter(Case.user_id == user_id)

    if materia:
        query = query.filter(Case.materia == materia)
    if complexidade:
        query = query.filter(Case.complexidade == complexidade)
    if search:
        like_term = f"%{search}%"
        query = query.filter(
            (Case.caso_id.ilike(like_term))
            | (Case.cliente_nome.ilike(like_term))
            | (Case.materia.ilike(like_term))
        )

    total = query.count()
    cases = (
        query.order_by(Case.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return cases, total
