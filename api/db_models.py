"""SQLAlchemy ORM models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return uuid.uuid4().hex


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_new_id)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=True)
    nome = Column(String, nullable=False)
    role = Column(String, nullable=False, default="consulta")  # admin | manager | consulta
    created_at = Column(DateTime, default=_utcnow)

    cases = relationship("Case", back_populates="user")


class Case(Base):
    __tablename__ = "cases"

    id = Column(String, primary_key=True, default=_new_id)
    caso_id = Column(String, nullable=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    briefing = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="pending")
    materia = Column(String, nullable=True)
    complexidade = Column(String, nullable=True)
    cliente_nome = Column(String, nullable=True)
    resumo = Column(Text, nullable=True)
    ficha_json = Column(Text, nullable=True)  # JSON string
    panorama_md = Column(Text, nullable=True)
    output_completo_md = Column(Text, nullable=True)
    alerta_complexo = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    processed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="cases")
    documents = relationship("Document", back_populates="case")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=_new_id)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    tipo = Column(String, nullable=False)  # upload | procuracao | contrato | panorama | ficha
    nome_arquivo = Column(String, nullable=False)
    caminho = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    tamanho = Column(Integer, default=0)
    created_at = Column(DateTime, default=_utcnow)

    case = relationship("Case", back_populates="documents")
