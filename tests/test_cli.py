import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from raphael_legal.cli import main
from raphael_legal.models import (
    CaseOutput,
    Complexidade,
    DocumentoGerado,
    FichaCaso,
    MateriaJuridica,
    ParteProcessual,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _mock_case_output() -> CaseOutput:
    return CaseOutput(
        ficha=FichaCaso(
            cliente=ParteProcessual(nome="João Silva", cpf_cnpj="12.345.678/0001-90"),
            materia=MateriaJuridica.MARCAS,
            complexidade=Complexidade.SIMPLES,
            justificativa_complexidade="Registro padrão",
            resumo="Registro de marca no INPI",
        ),
        panorama_md="## Panorama\nVia administrativa",
        documentos=[DocumentoGerado(tipo="procuracao_ad_judicia", conteudo_markdown="texto")],
        output_completo_md="# Output completo",
    )


class TestCLI:
    @patch("raphael_legal.cli.CaseProcessor")
    @patch("raphael_legal.cli.DocumentGenerator")
    def test_arquivo_existente(self, mock_doc_gen_cls, mock_processor_cls, capsys):
        mock_processor = MagicMock()
        mock_processor.process.return_value = _mock_case_output()
        mock_processor_cls.return_value = mock_processor

        mock_doc_gen = MagicMock()
        mock_doc_gen.generate.return_value = []
        mock_doc_gen_cls.return_value = mock_doc_gen

        briefing_file = FIXTURES_DIR / "briefing_marcas.txt"
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("raphael_legal.cli.Settings") as mock_settings_cls:
                settings = MagicMock()
                settings.ANTHROPIC_API_KEY = "test-key"
                settings.MODEL_NAME = "claude-sonnet-4-6"
                settings.OUTPUT_DIR = Path(tmpdir)
                settings.TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
                mock_settings_cls.return_value = settings

                sys.argv = ["raphael_legal", "processar", "--arquivo", str(briefing_file)]
                main()

                captured = capsys.readouterr()
                assert "Caso processado" in captured.out
                assert "Marcas" in captured.out

    def test_arquivo_inexistente(self, capsys):
        sys.argv = ["raphael_legal", "processar", "--arquivo", "/nao/existe.txt"]
        with patch("raphael_legal.cli.Settings") as mock_settings_cls:
            settings = MagicMock()
            settings.ANTHROPIC_API_KEY = "test-key"
            mock_settings_cls.return_value = settings

            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_sem_api_key(self):
        sys.argv = ["raphael_legal", "processar", "--texto", "teste"]
        with patch("raphael_legal.cli.Settings") as mock_settings_cls:
            settings = MagicMock()
            settings.ANTHROPIC_API_KEY = ""
            mock_settings_cls.return_value = settings

            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @patch("raphael_legal.cli.CaseProcessor")
    @patch("raphael_legal.cli.DocumentGenerator")
    def test_stdin(self, mock_doc_gen_cls, mock_processor_cls, capsys, monkeypatch):
        mock_processor = MagicMock()
        mock_processor.process.return_value = _mock_case_output()
        mock_processor_cls.return_value = mock_processor

        mock_doc_gen = MagicMock()
        mock_doc_gen.generate.return_value = []
        mock_doc_gen_cls.return_value = mock_doc_gen

        monkeypatch.setattr("sys.stdin", MagicMock(read=lambda: "briefing via stdin"))

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("raphael_legal.cli.Settings") as mock_settings_cls:
                settings = MagicMock()
                settings.ANTHROPIC_API_KEY = "test-key"
                settings.MODEL_NAME = "claude-sonnet-4-6"
                settings.OUTPUT_DIR = Path(tmpdir)
                settings.TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
                mock_settings_cls.return_value = settings

                sys.argv = ["raphael_legal", "processar", "--stdin"]
                main()

                captured = capsys.readouterr()
                assert "Caso processado" in captured.out
