import json
import re

from raphael_legal.models import (
    CaseOutput,
    Complexidade,
    DocumentoGerado,
    FichaCaso,
    MateriaJuridica,
    ParteProcessual,
)


def test_ficha_caso_id_format():
    ficha = FichaCaso(
        cliente=ParteProcessual(),
        materia=MateriaJuridica.MARCAS,
        complexidade=Complexidade.SIMPLES,
        justificativa_complexidade="Registro padrão",
        resumo="Teste",
    )
    assert re.match(r"^\d{8}-[a-f0-9]{6}$", ficha.caso_id)


def test_parte_processual_defaults():
    parte = ParteProcessual()
    assert "PENDENTE" in parte.nome
    assert "PENDENTE" in parte.cpf_cnpj
    assert "PENDENTE" in parte.contato
    assert "PENDENTE" in parte.endereco


def test_materia_juridica_enum():
    assert MateriaJuridica.MARCAS.value == "Marcas"
    assert MateriaJuridica.FAMILIA.value == "Família"


def test_complexidade_enum():
    assert Complexidade.SIMPLES.value == "Simples"
    assert Complexidade.MEDIO.value == "Médio"
    assert Complexidade.COMPLEXO.value == "Complexo"


def test_case_output_json_roundtrip():
    ficha = FichaCaso(
        cliente=ParteProcessual(nome="João Silva", cpf_cnpj="123.456.789-00"),
        materia=MateriaJuridica.MARCAS,
        complexidade=Complexidade.SIMPLES,
        justificativa_complexidade="Registro padrão de marca",
        resumo="Cliente quer registrar marca",
        documentos_recebidos=["comprovante CNPJ"],
        documentos_pendentes=["procuração"],
    )
    doc = DocumentoGerado(tipo="procuracao_ad_judicia", conteudo_markdown="# Procuração")
    output = CaseOutput(
        ficha=ficha,
        panorama_md="## Panorama",
        documentos=[doc],
        output_completo_md="# Completo",
    )

    json_str = output.model_dump_json()
    restored = CaseOutput.model_validate(json.loads(json_str))
    assert restored.ficha.cliente.nome == "João Silva"
    assert restored.documentos[0].tipo == "procuracao_ad_judicia"
