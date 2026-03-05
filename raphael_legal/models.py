from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

from pydantic import BaseModel, Field


class MateriaJuridica(str, Enum):
    MARCAS = "Marcas"
    PATENTES = "Patentes"
    FRANCHISING = "Franchising"
    CONSUMIDOR = "Consumidor"
    EMPRESARIAL = "Empresarial"
    FAMILIA = "Família"
    CIVIL = "Civil"
    OUTRO = "Outro"


class Complexidade(str, Enum):
    SIMPLES = "Simples"
    MEDIO = "Médio"
    COMPLEXO = "Complexo"


class ParteProcessual(BaseModel):
    nome: str = "⚠️ PENDENTE: nome"
    cpf_cnpj: str = "⚠️ PENDENTE: CPF/CNPJ"
    contato: str = "⚠️ PENDENTE: contato"
    endereco: str = "⚠️ PENDENTE: endereço"


class FichaCaso(BaseModel):
    caso_id: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y%m%d") + "-" + uuid.uuid4().hex[:6]
    )
    data_criacao: datetime = Field(default_factory=datetime.now)
    cliente: ParteProcessual
    parte_contraria: Optional[ParteProcessual] = None
    materia: MateriaJuridica
    complexidade: Complexidade
    justificativa_complexidade: str
    resumo: str
    documentos_recebidos: list[str] = []
    documentos_pendentes: list[str] = []
    alerta_complexo: Optional[str] = None


class DocumentoGerado(BaseModel):
    tipo: str
    conteudo_markdown: str
    arquivo_docx: Optional[str] = None


class CaseOutput(BaseModel):
    ficha: FichaCaso
    panorama_md: str
    documentos: list[DocumentoGerado]
    output_completo_md: str
