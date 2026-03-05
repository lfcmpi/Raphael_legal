import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from raphael_legal.models import MateriaJuridica, Complexidade
from raphael_legal.processor import (
    CaseProcessor,
    _build_ficha_from_tool_input,
    _normalize_materia,
    _parse_text_sections,
    _fallback_ficha_from_text,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_mock_response():
    data = json.loads((FIXTURES_DIR / "claude_response_marcas.json").read_text())
    # Build mock response object matching anthropic SDK structure
    response = MagicMock()
    blocks = []
    for block_data in data["content"]:
        block = MagicMock()
        block.type = block_data["type"]
        if block_data["type"] == "tool_use":
            block.name = block_data["name"]
            block.input = block_data["input"]
        elif block_data["type"] == "text":
            block.text = block_data["text"]
        blocks.append(block)
    response.content = blocks
    return response


class TestBuildFichaFromToolInput:
    def test_complete_data(self):
        data = json.loads((FIXTURES_DIR / "claude_response_marcas.json").read_text())
        tool_input = data["content"][0]["input"]
        ficha = _build_ficha_from_tool_input(tool_input)

        assert ficha.cliente.nome == "João Silva / JS Alimentos"
        assert ficha.cliente.cpf_cnpj == "12.345.678/0001-90"
        assert ficha.materia == MateriaJuridica.MARCAS
        assert ficha.complexidade == Complexidade.SIMPLES
        assert ficha.parte_contraria is None  # N/A
        assert len(ficha.documentos_recebidos) == 1
        assert len(ficha.documentos_pendentes) == 4

    def test_missing_fields_get_pendente(self):
        ficha = _build_ficha_from_tool_input({
            "materia": "Consumidor",
            "complexidade": "Médio",
            "justificativa_complexidade": "test",
            "resumo": "test",
            "documentos_recebidos": [],
            "documentos_pendentes": [],
        })
        assert "PENDENTE" in ficha.cliente.nome
        assert "PENDENTE" in ficha.cliente.cpf_cnpj


class TestNormalizeMateria:
    def test_exact_match(self):
        assert _normalize_materia("Marcas") == MateriaJuridica.MARCAS

    def test_lowercase(self):
        assert _normalize_materia("marcas") == MateriaJuridica.MARCAS

    def test_singular(self):
        assert _normalize_materia("marca") == MateriaJuridica.MARCAS

    def test_unknown(self):
        assert _normalize_materia("xyz") == MateriaJuridica.OUTRO

    def test_familia_without_accent(self):
        assert _normalize_materia("familia") == MateriaJuridica.FAMILIA


class TestParseTextSections:
    def test_extracts_panorama_and_docs(self):
        data = json.loads((FIXTURES_DIR / "claude_response_marcas.json").read_text())
        text = data["content"][1]["text"]
        panorama, docs = _parse_text_sections(text)

        assert "PANORAMA" in panorama.upper()
        assert len(docs) == 2
        assert docs[0].tipo == "procuracao_ad_judicia"
        assert docs[1].tipo == "contrato_honorarios"

    def test_empty_text(self):
        panorama, docs = _parse_text_sections("")
        assert panorama == ""
        assert docs == []


class TestFallback:
    def test_fallback_returns_pendente_ficha(self):
        ficha = _fallback_ficha_from_text("some random text")
        assert "PENDENTE" in ficha.cliente.nome
        assert ficha.materia == MateriaJuridica.OUTRO


class TestCaseProcessor:
    @patch("raphael_legal.processor.anthropic.Anthropic")
    def test_process_with_tool_use(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _load_mock_response()

        processor = CaseProcessor(api_key="test-key")
        result = processor.process("briefing de teste")

        assert result.ficha.materia == MateriaJuridica.MARCAS
        assert result.ficha.cliente.nome == "João Silva / JS Alimentos"
        assert "PANORAMA" in result.panorama_md.upper()
        assert len(result.documentos) == 2
        assert result.output_completo_md != ""

    @patch("raphael_legal.processor.anthropic.Anthropic")
    def test_process_without_tool_use_fallback(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        # Response with only text, no tool_use
        response = MagicMock()
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "## 1. FICHA\nAlguns dados\n## 2. PANORAMA\nVia admin\n## 3. DOCUMENTOS\n### 3A. Procuração\nTexto"
        response.content = [text_block]
        mock_client.messages.create.return_value = response

        processor = CaseProcessor(api_key="test-key")
        result = processor.process("briefing vazio")

        assert "PENDENTE" in result.ficha.cliente.nome
        assert result.ficha.materia == MateriaJuridica.OUTRO

    @patch("raphael_legal.processor.anthropic.Anthropic")
    def test_empty_briefing_no_crash(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _load_mock_response()

        processor = CaseProcessor(api_key="test-key")
        result = processor.process("")
        assert result.ficha is not None
