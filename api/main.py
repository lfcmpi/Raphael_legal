"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database import engine
from api.db_models import Base
from api.routes.auth_routes import router as auth_router
from api.routes.cases_routes import router as cases_router
from api.routes.documents_routes import router as documents_router
from api.routes.users_routes import router as users_router
from api.routes.settings_routes import router as settings_router
from api.routes.templates_routes import router as templates_router, case_templates_router

_default_origins = "http://localhost:5173,http://localhost:3000"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", _default_origins).split(",")


def _seed_default_templates():
    """Seed built-in templates if they don't exist yet."""
    import json
    from api.database import SessionLocal
    from api.db_models import Template

    db = SessionLocal()
    try:
        existing = db.query(Template).filter(Template.categoria.in_(["procuracao", "contrato"])).count()
        if existing > 0:
            return

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        templates_dir = os.path.join(project_root, "templates")

        defaults = [
            {
                "nome": "Procuracao Ad Judicia",
                "descricao": "Procuracao outorgando poderes ao advogado para representacao judicial (ad judicia). Documento padrao para qualquer tipo de acao judicial.",
                "categoria": "procuracao",
                "materias_aplicaveis": json.dumps(["Marcas", "Patentes", "Franchising", "Consumidor", "Empresarial", "Familia", "Civil", "Outro"]),
                "caminho_docx": os.path.join(templates_dir, "procuracao_ad_judicia.docx"),
            },
            {
                "nome": "Contrato de Honorarios",
                "descricao": "Contrato de prestacao de servicos advocaticios com clausulas de honorarios, vigencia, sigilo e foro. Aplicavel a qualquer materia juridica.",
                "categoria": "contrato",
                "materias_aplicaveis": json.dumps(["Marcas", "Patentes", "Franchising", "Consumidor", "Empresarial", "Familia", "Civil", "Outro"]),
                "caminho_docx": os.path.join(templates_dir, "contrato_honorarios.docx"),
            },
        ]

        for d in defaults:
            t = Template(**d)
            db.add(t)
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _seed_default_templates()
    yield


app = FastAPI(
    title="Raphael Legal API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(cases_router)
app.include_router(documents_router)
app.include_router(users_router)
app.include_router(settings_router)
app.include_router(templates_router)
app.include_router(case_templates_router)
