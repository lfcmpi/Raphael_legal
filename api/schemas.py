"""Pydantic schemas for API request/response."""

from datetime import datetime

from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class GoogleLoginRequest(BaseModel):
    credential: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: str
    email: str
    nome: str
    role: str

    model_config = {"from_attributes": True}


# --- Cases ---


class CaseCreateRequest(BaseModel):
    briefing: str


class CaseUpdateRequest(BaseModel):
    caso_id: str | None = None
    materia: str | None = None
    complexidade: str | None = None
    cliente_nome: str | None = None
    resumo: str | None = None
    alerta_complexo: str | None = None
    briefing: str | None = None
    panorama_md: str | None = None
    ficha_json: dict | None = None


class DocumentInfo(BaseModel):
    id: str
    tipo: str
    nome_arquivo: str
    tamanho: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CaseSummary(BaseModel):
    id: str
    caso_id: str | None
    status: str
    materia: str | None
    complexidade: str | None
    cliente_nome: str | None
    resumo: str | None
    alerta_complexo: str | None
    created_at: datetime
    processed_at: datetime | None

    model_config = {"from_attributes": True}


class CaseDetail(CaseSummary):
    briefing: str
    ficha_json: dict | None = None
    panorama_md: str | None
    output_completo_md: str | None
    documentos: list[DocumentInfo] = []


class CaseListResponse(BaseModel):
    cases: list[CaseSummary]
    total: int


class CaseStatusResponse(BaseModel):
    status: str
    progress: str


# --- Users ---


class UserSummary(BaseModel):
    id: str
    email: str
    nome: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    users: list[UserSummary]
    total: int


class UserCreateRequest(BaseModel):
    email: str
    nome: str
    password: str
    role: str = "consulta"


class UserUpdateRequest(BaseModel):
    email: str | None = None
    nome: str | None = None
    password: str | None = None
    role: str | None = None
