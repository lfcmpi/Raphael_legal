"""End-to-end integration test with mocked Claude API."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from raphael_legal.config import Settings
from raphael_legal.document_generator import DocumentGenerator
from raphael_legal.processor import CaseProcessor

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def _load_mock_response():
    data = json.loads((FIXTURES_DIR / "claude_response_marcas.json").read_text())
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


class TestIntegrationPipeline:
    @patch("raphael_legal.processor.anthropic.Anthropic")
    def test_full_pipeline_marcas(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _load_mock_response()

        briefing = (FIXTURES_DIR / "briefing_marcas.txt").read_text()

        # Process
        processor = CaseProcessor(api_key="test-key")
        result = processor.process(briefing)

        # Verify ficha
        assert result.ficha.materia.value == "Marcas"
        assert result.ficha.cliente.nome == "João Silva / JS Alimentos"
        assert result.ficha.cliente.cpf_cnpj == "12.345.678/0001-90"
        assert result.ficha.complexidade.value == "Simples"

        # Verify panorama
        assert result.panorama_md != ""
        assert "VERIFICAR" in result.panorama_md

        # Verify documents exist
        assert len(result.documentos) == 2

        # Generate DOCX
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / result.ficha.caso_id
            doc_gen = DocumentGenerator(TEMPLATES_DIR)
            paths = doc_gen.generate(result, output_dir)

            # Verify files
            assert (output_dir / "procuracao.docx").exists()
            assert (output_dir / "procuracao.docx").stat().st_size > 0
            assert (output_dir / "contrato_honorarios.docx").exists()
            assert (output_dir / "contrato_honorarios.docx").stat().st_size > 0

            # Save ficha.json
            ficha_path = output_dir / "ficha.json"
            ficha_path.write_text(result.ficha.model_dump_json(indent=2))
            ficha_data = json.loads(ficha_path.read_text())
            assert ficha_data["materia"] == "Marcas"

            # Save panorama
            panorama_path = output_dir / "panorama.md"
            panorama_path.write_text(result.panorama_md)
            assert panorama_path.stat().st_size > 0

    @patch("raphael_legal.processor.anthropic.Anthropic")
    def test_no_invented_data(self, mock_anthropic_cls):
        """CPF/CNPJ in output must exist in input or be PENDENTE."""
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _load_mock_response()

        briefing = (FIXTURES_DIR / "briefing_marcas.txt").read_text()
        processor = CaseProcessor(api_key="test-key")
        result = processor.process(briefing)

        cpf_cnpj = result.ficha.cliente.cpf_cnpj
        # Must be from the input or PENDENTE
        assert cpf_cnpj in briefing or "PENDENTE" in cpf_cnpj

    @patch("raphael_legal.processor.anthropic.Anthropic")
    def test_minimal_briefing_mostly_pendente(self, mock_anthropic_cls):
        """Minimal input: response with tool_use should work. Fallback tested separately."""
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        # Simulate a response with mostly PENDENTE fields
        response = MagicMock()
        tool_block = MagicMock()
        tool_block.type = "tool_use"
        tool_block.name = "extrair_ficha_caso"
        tool_block.input = {
            "cliente_nome": "⚠️ PENDENTE: nome do cliente",
            "cliente_cpf_cnpj": "⚠️ PENDENTE: CPF/CNPJ",
            "cliente_contato": "⚠️ PENDENTE: contato",
            "cliente_endereco": "⚠️ PENDENTE: endereço",
            "parte_contraria_nome": "N/A",
            "materia": "Marcas",
            "complexidade": "Simples",
            "justificativa_complexidade": "Informações insuficientes para avaliar complexidade real.",
            "resumo": "Cliente deseja registrar uma marca. Sem detalhes adicionais fornecidos.",
            "documentos_recebidos": [],
            "documentos_pendentes": [
                "Dados completos do cliente",
                "Nome e logomarca pretendida",
                "Classe NCL desejada",
                "Procuração assinada",
            ],
        }
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "## 2. PANORAMA ESTRATÉGICO\n\nInformações insuficientes.\n\n## 3. DOCUMENTOS\n\n### 3A. Procuração\nTexto\n### 3B. Contrato\nTexto"
        response.content = [tool_block, text_block]
        mock_client.messages.create.return_value = response

        briefing = (FIXTURES_DIR / "briefing_minimal.txt").read_text()
        processor = CaseProcessor(api_key="test-key")
        result = processor.process(briefing)

        # Most fields should be PENDENTE
        assert "PENDENTE" in result.ficha.cliente.nome
        assert "PENDENTE" in result.ficha.cliente.cpf_cnpj
        assert len(result.ficha.documentos_pendentes) >= 3

    @patch("raphael_legal.processor.anthropic.Anthropic")
    def test_all_fixtures_process_without_crash(self, mock_anthropic_cls):
        """All fixture files should be processable."""
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _load_mock_response()

        processor = CaseProcessor(api_key="test-key")

        for fixture_file in FIXTURES_DIR.glob("briefing_*.txt"):
            briefing = fixture_file.read_text()
            result = processor.process(briefing)
            assert result.ficha is not None
            assert result.ficha.caso_id is not None
