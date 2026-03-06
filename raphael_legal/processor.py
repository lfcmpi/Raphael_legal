import logging
import re

import anthropic

from raphael_legal.config import Settings
from raphael_legal.models import (
    CaseOutput,
    Complexidade,
    DocumentoGerado,
    FichaCaso,
    MateriaJuridica,
    ParteProcessual,
)
from raphael_legal.prompts import build_api_params

logger = logging.getLogger(__name__)

_MATERIA_MAP = {
    "marcas": MateriaJuridica.MARCAS,
    "marca": MateriaJuridica.MARCAS,
    "patentes": MateriaJuridica.PATENTES,
    "patente": MateriaJuridica.PATENTES,
    "franchising": MateriaJuridica.FRANCHISING,
    "consumidor": MateriaJuridica.CONSUMIDOR,
    "empresarial": MateriaJuridica.EMPRESARIAL,
    "família": MateriaJuridica.FAMILIA,
    "familia": MateriaJuridica.FAMILIA,
    "civil": MateriaJuridica.CIVIL,
}


def _normalize_materia(raw: str) -> MateriaJuridica:
    key = raw.strip().lower()
    if key in _MATERIA_MAP:
        return _MATERIA_MAP[key]
    try:
        return MateriaJuridica(raw.strip())
    except ValueError:
        return MateriaJuridica.OUTRO


def _normalize_complexidade(raw: str) -> Complexidade:
    key = raw.strip().lower()
    mapping = {"simples": Complexidade.SIMPLES, "médio": Complexidade.MEDIO, "medio": Complexidade.MEDIO, "complexo": Complexidade.COMPLEXO}
    if key in mapping:
        return mapping[key]
    try:
        return Complexidade(raw.strip())
    except ValueError:
        return Complexidade.MEDIO


def _build_ficha_from_tool_input(data: dict) -> FichaCaso:
    cliente = ParteProcessual(
        nome=data.get("cliente_nome", "⚠️ PENDENTE: nome"),
        cpf_cnpj=data.get("cliente_cpf_cnpj", "⚠️ PENDENTE: CPF/CNPJ"),
        contato=data.get("cliente_contato", "⚠️ PENDENTE: contato"),
        endereco=data.get("cliente_endereco", "⚠️ PENDENTE: endereço"),
    )

    parte_contraria = None
    pc_nome = data.get("parte_contraria_nome", "")
    if pc_nome and pc_nome not in ("N/A", "n/a"):
        parte_contraria = ParteProcessual(
            nome=pc_nome,
            cpf_cnpj=data.get("parte_contraria_cpf_cnpj", "⚠️ PENDENTE: CPF/CNPJ"),
        )

    return FichaCaso(
        cliente=cliente,
        parte_contraria=parte_contraria,
        materia=_normalize_materia(data.get("materia", "Outro")),
        complexidade=_normalize_complexidade(data.get("complexidade", "Médio")),
        justificativa_complexidade=data.get("justificativa_complexidade", "⚠️ PENDENTE"),
        resumo=data.get("resumo", "⚠️ PENDENTE"),
        documentos_recebidos=data.get("documentos_recebidos", []),
        documentos_pendentes=data.get("documentos_pendentes", []),
        alerta_complexo=data.get("alerta_complexo"),
    )


def _parse_text_sections(text: str) -> tuple[str, list[DocumentoGerado]]:
    panorama = ""
    documentos: list[DocumentoGerado] = []

    # Try multiple header patterns for panorama section
    panorama_match = re.search(
        r"(##\s*2[\.\s\-—]+.*?PANORAMA.*?)(?=##\s*3[\.\s\-—]|$)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if not panorama_match:
        # Fallback: any "PANORAMA" header followed by content
        panorama_match = re.search(
            r"(#+\s*.*?PANORAMA\s+ESTRAT[ÉE]GICO.*?)(?=#+\s*.*?DOCUMENTO|$)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
    if not panorama_match:
        # Last resort: section 2 with any title
        panorama_match = re.search(
            r"(##\s*2\..*?)(?=##\s*3\.|$)",
            text,
            re.DOTALL,
        )
    if panorama_match:
        panorama = panorama_match.group(1).strip()
        logger.info("Panorama extraído com %d caracteres", len(panorama))
    else:
        logger.warning(
            "Panorama não encontrado no texto. Headers encontrados: %s",
            re.findall(r"^#{1,4}\s.*$", text, re.MULTILINE),
        )

    docs_match = re.search(r"##\s*3[\.\s\-—].*", text, re.DOTALL)
    if not docs_match:
        docs_match = re.search(r"#+\s*.*?DOCUMENTO.*", text, re.DOTALL | re.IGNORECASE)
    if docs_match:
        docs_text = docs_match.group(0)
        # Split by sub-headers (### 3A., ### 3B., etc.)
        sub_docs = re.split(r"(?=### 3[A-Z]\.)", docs_text)
        for sub in sub_docs:
            sub = sub.strip()
            if not sub or sub.startswith("## 3."):
                continue
            # Determine tipo from header
            tipo = "documento"
            if "procuração" in sub.lower() or "procuracao" in sub.lower():
                tipo = "procuracao_ad_judicia"
            elif "contrato" in sub.lower() and "honorários" in sub.lower():
                tipo = "contrato_honorarios"
            elif "notificação" in sub.lower() or "notificacao" in sub.lower():
                tipo = "notificacao"
            elif "petição" in sub.lower() or "peticao" in sub.lower():
                tipo = "peticao"
            documentos.append(DocumentoGerado(tipo=tipo, conteudo_markdown=sub))

    return panorama, documentos


def _fallback_ficha_from_text(text: str) -> FichaCaso:
    logger.warning("Claude não usou tool_use, tentando regex fallback")
    return FichaCaso(
        cliente=ParteProcessual(),
        materia=MateriaJuridica.OUTRO,
        complexidade=Complexidade.MEDIO,
        justificativa_complexidade="⚠️ PENDENTE: extraído via fallback",
        resumo="⚠️ PENDENTE: extração automática falhou, revisar output completo",
    )


def _build_client(api_key: str) -> anthropic.Anthropic:
    if api_key.startswith("sk-ant-oat"):
        return anthropic.Anthropic(auth_token=api_key)
    return anthropic.Anthropic(api_key=api_key)


class CaseProcessor:
    def __init__(self, api_key: str, model: str | None = None) -> None:
        self._client = _build_client(api_key)
        self._settings = Settings()
        if model:
            self._settings.MODEL_NAME = model

    def process(self, briefing: str) -> CaseOutput:
        params = build_api_params(briefing, self._settings)
        response = self._client.messages.create(**params)

        ficha = None
        text_parts: list[str] = []

        for block in response.content:
            if block.type == "tool_use" and block.name == "extrair_ficha_caso":
                ficha = _build_ficha_from_tool_input(block.input)
            elif block.type == "text":
                text_parts.append(block.text)

        # When Claude uses tool_use, stop_reason="tool_use" and it stops.
        # We need to send tool_result(s) so Claude continues with Stages 2 and 3.
        # Handle multiple rounds if Claude makes additional tool calls.
        messages = [{"role": "user", "content": briefing}]
        current_response = response
        max_continuations = 3

        for turn in range(max_continuations):
            if current_response.stop_reason != "tool_use":
                break

            tool_use_blocks = [
                b for b in current_response.content if b.type == "tool_use"
            ]
            if not tool_use_blocks:
                break

            logger.info(
                "Turn %d: enviando tool_result para %d tool(s)",
                turn + 1,
                len(tool_use_blocks),
            )

            # Build tool results for all tool_use blocks
            tool_results = []
            for tb in tool_use_blocks:
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tb.id,
                    "content": "Ficha registrada com sucesso. Prossiga com a Etapa 2 (Panorama Estrategico) e Etapa 3 (Documentos).",
                })

            messages.append({"role": "assistant", "content": current_response.content})
            messages.append({"role": "user", "content": tool_results})

            continuation = self._client.messages.create(
                model=params["model"],
                max_tokens=params["max_tokens"],
                system=params["system"],
                messages=messages,
                tools=params["tools"],
                tool_choice={"type": "auto"},
            )
            logger.info(
                "Continuation turn %d: stop_reason=%s, blocks=%d",
                turn + 1,
                continuation.stop_reason,
                len(continuation.content),
            )
            for block in continuation.content:
                if block.type == "text":
                    text_parts.append(block.text)
                    logger.info("Continuation text block: %d chars", len(block.text))
                elif block.type == "tool_use" and block.name == "extrair_ficha_caso":
                    if ficha is None:
                        ficha = _build_ficha_from_tool_input(block.input)

            current_response = continuation

        if current_response.stop_reason == "max_tokens":
            logger.warning("Resposta truncada por max_tokens — panorama pode estar incompleto")

        full_text = "\n\n".join(text_parts)
        logger.info(
            "full_text: %d chars, %d text_parts",
            len(full_text),
            len(text_parts),
        )

        if ficha is None:
            ficha = _fallback_ficha_from_text(full_text)

        panorama, documentos = _parse_text_sections(full_text)
        logger.info(
            "Resultado: panorama=%d chars, documentos=%d",
            len(panorama),
            len(documentos),
        )

        return CaseOutput(
            ficha=ficha,
            panorama_md=panorama,
            documentos=documentos,
            output_completo_md=full_text,
        )
