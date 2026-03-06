"""
Teste do CaseProcessor corrigido - valida que panorama e documentos sao gerados.

Uso:
    ANTHROPIC_API_KEY=sk-... python3 tests/test_processor_fix.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from raphael_legal.processor import CaseProcessor

BRIEFING_CONSUMIDOR = """
Cliente: Maria Silva, CPF 123.456.789-00, tel (11) 98765-4321, mora na Rua das Flores 100, Sao Paulo/SP.

Comprou um notebook Dell no site da Loja TechBR (CNPJ 12.345.678/0001-99) em 15/01/2025 por R$ 4.500,00.
O produto apresentou defeito na tela apos 20 dias de uso. Entrou em contato com a loja que se recusou a trocar,
alegando mau uso. O cliente tem nota fiscal e prints das conversas com o SAC.

Quer trocar o produto ou receber o dinheiro de volta, alem de indenizacao pelo transtorno.
"""

BRIEFING_MARCAS = """
A empresa Cafe Aroma Ltda (CNPJ 98.765.432/0001-11), representada por Joao Pereira,
tel (21) 99876-5432, email joao@cafearoma.com.br, Rua do Comercio 50, Rio de Janeiro/RJ.

Descobriu que um concorrente (Cafe Aroma Premium, sem CNPJ identificado) esta usando marca
praticamente identica ("Cafe Aroma") em embalagens de cafe vendidas no RJ e SP.
A empresa cliente tem registro de marca no INPI desde 2019 (processo nr 912345678).

Documentos disponiveis: certificado de registro INPI, fotos das embalagens do concorrente,
nota fiscal da empresa cliente.

Quer que o concorrente pare de usar a marca e pague indenizacao.
"""

BRIEFING_FAMILIA = """
Pedro Santos, CPF 987.654.321-00, tel (31) 91234-5678, Belo Horizonte/MG.

Separou da esposa Ana Oliveira ha 6 meses. Tem 2 filhos menores (8 e 12 anos).
Quer formalizar o divorcio consensual — ja ha acordo sobre guarda compartilhada
e pensao de 30% do salario liquido. Nao ha imoveis, apenas um carro que ficara com a esposa.

Tem certidao de casamento e certidoes de nascimento dos filhos.
"""


def test_case(briefing: str, label: str) -> bool:
    print(f"\n{'='*60}")
    print(f"TESTE: {label}")
    print(f"{'='*60}")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERRO: ANTHROPIC_API_KEY nao definida")
        sys.exit(1)

    processor = CaseProcessor(api_key=api_key)
    result = processor.process(briefing)

    # Validar ficha
    ficha = result.ficha
    print(f"\n  Ficha:")
    print(f"    cliente: {ficha.cliente.nome}")
    print(f"    materia: {ficha.materia.value}")
    print(f"    complexidade: {ficha.complexidade.value}")
    print(f"    resumo: {ficha.resumo[:100]}...")

    # Validar panorama
    print(f"\n  Panorama: {len(result.panorama_md)} chars")
    if result.panorama_md:
        print(f"    Preview: {result.panorama_md[:200]}...")
    else:
        print("    >>> VAZIO - FALHOU <<<")

    # Validar documentos
    print(f"\n  Documentos: {len(result.documentos)}")
    for d in result.documentos:
        print(f"    - {d.tipo}: {len(d.conteudo_markdown)} chars")

    # Validar output completo
    print(f"\n  Output completo: {len(result.output_completo_md)} chars")

    ok = (
        len(result.panorama_md) > 100
        and len(result.documentos) >= 2
        and ficha.cliente.nome != "PENDENTE: nome"
    )
    print(f"\n  RESULTADO: {'PASSOU' if ok else 'FALHOU'}")
    return ok


if __name__ == "__main__":
    if "--all" in sys.argv:
        tests = [
            (BRIEFING_CONSUMIDOR, "Consumidor"),
            (BRIEFING_MARCAS, "Marcas"),
            (BRIEFING_FAMILIA, "Familia"),
        ]
    else:
        tests = [(BRIEFING_CONSUMIDOR, "Consumidor")]

    results = []
    for briefing, label in tests:
        ok = test_case(briefing, label)
        results.append((label, ok))

    print(f"\n{'='*60}")
    print("RESUMO FINAL")
    print(f"{'='*60}")
    all_ok = True
    for label, ok in results:
        status = "PASSOU" if ok else "FALHOU"
        print(f"  {label}: {status}")
        if not ok:
            all_ok = False

    print(f"\n  {'TODOS OS TESTES PASSARAM' if all_ok else 'ALGUNS TESTES FALHARAM'}")
