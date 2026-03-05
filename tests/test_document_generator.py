import tempfile
from pathlib import Path

import pytest

from raphael_legal.document_generator import DocumentGenerator
from raphael_legal.models import (
    CaseOutput,
    Complexidade,
    DocumentoGerado,
    FichaCaso,
    MateriaJuridica,
    ParteProcessual,
)

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def _make_case_output(cliente: ParteProcessual | None = None) -> CaseOutput:
    if cliente is None:
        cliente = ParteProcessual(
            nome="João Silva",
            cpf_cnpj="12.345.678/0001-90",
            contato="(11) 99999-0000",
            endereco="Rua das Flores, 123, São Paulo/SP",
        )
    return CaseOutput(
        ficha=FichaCaso(
            cliente=cliente,
            materia=MateriaJuridica.MARCAS,
            complexidade=Complexidade.SIMPLES,
            justificativa_complexidade="Registro padrão",
            resumo="Registro de marca Café Premium no INPI",
        ),
        panorama_md="## Panorama",
        documentos=[],
        output_completo_md="# Completo",
    )


class TestDocumentGenerator:
    def test_generates_procuracao_with_complete_data(self):
        gen = DocumentGenerator(TEMPLATES_DIR)
        case_output = _make_case_output()
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = gen.generate(case_output, Path(tmpdir))
            assert len(paths) == 2
            procuracao = paths[0]
            assert procuracao.name == "procuracao.docx"
            assert procuracao.stat().st_size > 0

    def test_generates_procuracao_with_pendente_fields(self):
        gen = DocumentGenerator(TEMPLATES_DIR)
        case_output = _make_case_output(cliente=ParteProcessual())
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = gen.generate(case_output, Path(tmpdir))
            assert paths[0].stat().st_size > 0

    def test_generates_contrato(self):
        gen = DocumentGenerator(TEMPLATES_DIR)
        case_output = _make_case_output()
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = gen.generate(case_output, Path(tmpdir))
            contrato = paths[1]
            assert contrato.name == "contrato_honorarios.docx"
            assert contrato.stat().st_size > 0

    def test_creates_output_dir(self):
        gen = DocumentGenerator(TEMPLATES_DIR)
        case_output = _make_case_output()
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = Path(tmpdir) / "sub" / "dir"
            paths = gen.generate(case_output, nested)
            assert nested.exists()
            assert len(paths) == 2
