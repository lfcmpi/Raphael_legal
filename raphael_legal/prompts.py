from pathlib import Path

from raphael_legal.config import Settings

_INSUMOS_DIR = Path(__file__).parent.parent / "insumos"
_PROMPT_FILE = _INSUMOS_DIR / "prompt-legal-case-processor.md"

_TOOL_USE_INSTRUCTION = (
    "\n\n---\n\n"
    "**INSTRUÇÃO ADICIONAL:** Ao processar a Etapa 1 (Ficha do Caso), "
    "use a ferramenta `extrair_ficha_caso` para registrar os dados estruturados. "
    "Depois continue com as Etapas 2 e 3 como texto."
)


def _load_system_prompt() -> str:
    if _PROMPT_FILE.exists():
        return _PROMPT_FILE.read_text(encoding="utf-8") + _TOOL_USE_INSTRUCTION
    return (
        "Você é um sistema de processamento jurídico brasileiro. "
        "Processe o briefing em 3 etapas: 1) Ficha do Caso (use a ferramenta extrair_ficha_caso), "
        "2) Panorama Estratégico, 3) Documentos. "
        "Marque dados ausentes com ⚠️ PENDENTE e citações legais com [VERIFICAR]."
    )


SYSTEM_PROMPT = _load_system_prompt()

FICHA_TOOL_SCHEMA = {
    "name": "extrair_ficha_caso",
    "description": "Registra a ficha estruturada do caso jurídico extraída do briefing.",
    "input_schema": {
        "type": "object",
        "required": [
            "cliente_nome",
            "materia",
            "complexidade",
            "justificativa_complexidade",
            "resumo",
            "documentos_recebidos",
            "documentos_pendentes",
        ],
        "properties": {
            "cliente_nome": {
                "type": "string",
                "description": "Nome completo do cliente. Se ausente, usar '⚠️ PENDENTE: nome do cliente'",
            },
            "cliente_cpf_cnpj": {
                "type": "string",
                "description": "CPF ou CNPJ do cliente. Se ausente, usar '⚠️ PENDENTE: CPF/CNPJ'",
            },
            "cliente_contato": {
                "type": "string",
                "description": "Telefone ou email do cliente. Se ausente, usar '⚠️ PENDENTE: contato'",
            },
            "cliente_endereco": {
                "type": "string",
                "description": "Endereço completo do cliente. Se ausente, usar '⚠️ PENDENTE: endereço'",
            },
            "parte_contraria_nome": {
                "type": "string",
                "description": "Nome da parte contrária. 'N/A' se não aplicável. '⚠️ PENDENTE' se deveria ter mas não foi informado.",
            },
            "parte_contraria_cpf_cnpj": {
                "type": "string",
                "description": "CPF/CNPJ da parte contrária. 'N/A' se não aplicável.",
            },
            "materia": {
                "type": "string",
                "enum": [
                    "Marcas",
                    "Patentes",
                    "Franchising",
                    "Consumidor",
                    "Empresarial",
                    "Família",
                    "Civil",
                    "Outro",
                ],
            },
            "complexidade": {
                "type": "string",
                "enum": ["Simples", "Médio", "Complexo"],
            },
            "justificativa_complexidade": {
                "type": "string",
                "description": "1 frase justificando a classificação de complexidade",
            },
            "resumo": {
                "type": "string",
                "description": "Máximo 5 frases: fatos → problema → pretensão do cliente",
            },
            "documentos_recebidos": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lista de documentos fornecidos no briefing",
            },
            "documentos_pendentes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lista de documentos que faltam para prosseguir",
            },
            "alerta_complexo": {
                "type": "string",
                "description": "Preenchido APENAS se complexidade='Complexo'. Formato: '🔴 CASO COMPLEXO — Recomenda-se análise aprofundada antes de prosseguir. Considerar: [motivo]'",
            },
        },
    },
}


def build_api_params(briefing: str, settings: Settings | None = None) -> dict:
    if settings is None:
        settings = Settings()
    return {
        "model": settings.MODEL_NAME,
        "max_tokens": 16384,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": briefing}],
        "tools": [FICHA_TOOL_SCHEMA],
        "tool_choice": {"type": "auto"},
    }
