"""
Teste de diagnóstico: verifica por que o panorama estratégico vem vazio.

Hipótese: quando Claude usa tool_use para a Etapa 1, a API retorna com
stop_reason="tool_use" e PARA. O código nunca envia tool_result,
então as Etapas 2 e 3 nunca são geradas.

Uso:
    ANTHROPIC_API_KEY=sk-... python tests/test_panorama_debug.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import anthropic

from raphael_legal.prompts import build_api_params, SYSTEM_PROMPT, FICHA_TOOL_SCHEMA
from raphael_legal.processor import _parse_text_sections, _build_ficha_from_tool_input

# --- Briefings fictícios para teste ---

BRIEFING_CONSUMIDOR = """
Cliente: Maria Silva, CPF 123.456.789-00, tel (11) 98765-4321, mora na Rua das Flores 100, São Paulo/SP.

Comprou um notebook Dell no site da Loja TechBR (CNPJ 12.345.678/0001-99) em 15/01/2025 por R$ 4.500,00.
O produto apresentou defeito na tela após 20 dias de uso. Entrou em contato com a loja que se recusou a trocar,
alegando mau uso. O cliente tem nota fiscal e prints das conversas com o SAC.

Quer trocar o produto ou receber o dinheiro de volta, além de indenização pelo transtorno.
"""

BRIEFING_MARCAS = """
A empresa Café Aroma Ltda (CNPJ 98.765.432/0001-11), representada por João Pereira,
tel (21) 99876-5432, email joao@cafearoma.com.br, Rua do Comércio 50, Rio de Janeiro/RJ.

Descobriu que um concorrente (Café Aroma Premium, sem CNPJ identificado) está usando marca
praticamente idêntica ("Café Aroma") em embalagens de café vendidas no RJ e SP.
A empresa cliente tem registro de marca no INPI desde 2019 (processo nº 912345678).

Documentos disponíveis: certificado de registro INPI, fotos das embalagens do concorrente,
nota fiscal da empresa cliente.

Quer que o concorrente pare de usar a marca e pague indenização.
"""

BRIEFING_FAMILIA = """
Pedro Santos, CPF 987.654.321-00, tel (31) 91234-5678, Belo Horizonte/MG.

Separou da esposa Ana Oliveira há 6 meses. Tem 2 filhos menores (8 e 12 anos).
Quer formalizar o divórcio consensual — já há acordo sobre guarda compartilhada
e pensão de 30% do salário líquido. Não há imóveis, apenas um carro que ficará com a esposa.

Tem certidão de casamento e certidões de nascimento dos filhos.
"""


def run_test(briefing: str, label: str):
    print(f"\n{'='*70}")
    print(f"TESTE: {label}")
    print(f"{'='*70}")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERRO: ANTHROPIC_API_KEY nao definida")
        sys.exit(1)

    if api_key.startswith("sk-ant-oat"):
        client = anthropic.Anthropic(auth_token=api_key)
    else:
        client = anthropic.Anthropic(api_key=api_key)

    params = build_api_params(briefing)

    print(f"\n[1] Chamando API Claude ({params['model']})...")
    response = client.messages.create(**params)

    print(f"\n[2] stop_reason: {response.stop_reason}")
    print(f"    content blocks: {len(response.content)}")

    ficha_data = None
    text_parts = []

    for i, block in enumerate(response.content):
        print(f"    block[{i}]: type={block.type}", end="")
        if block.type == "tool_use":
            print(f", name={block.name}")
            ficha_data = block.input
        elif block.type == "text":
            print(f", len={len(block.text)} chars")
            text_parts.append(block.text)

    full_text = "\n\n".join(text_parts)

    print(f"\n[3] Texto total: {len(full_text)} chars")
    if full_text:
        print(f"    Primeiros 200 chars: {full_text[:200]}...")
    else:
        print("    >>> TEXTO VAZIO <<<")

    # Parse panorama
    panorama, documentos = _parse_text_sections(full_text)
    print(f"\n[4] Panorama extraido: {len(panorama)} chars")
    if panorama:
        print(f"    Primeiros 300 chars: {panorama[:300]}...")
    else:
        print("    >>> PANORAMA VAZIO <<<")

    print(f"    Documentos extraidos: {len(documentos)}")
    for d in documentos:
        print(f"      - {d.tipo}: {len(d.conteudo_markdown)} chars")

    # Se stop_reason = tool_use, testar continuação
    if response.stop_reason == "tool_use":
        print(f"\n[5] stop_reason=tool_use confirmado!")
        print("    O Claude PAROU apos o tool_use. Etapas 2 e 3 nao foram geradas.")
        print("    Testando continuacao com tool_result...")

        # Encontrar o tool_use block
        tool_use_block = next(b for b in response.content if b.type == "tool_use")

        continuation_messages = [
            {"role": "user", "content": briefing},
            {"role": "assistant", "content": response.content},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_block.id,
                        "content": "Ficha registrada com sucesso. Prossiga com a Etapa 2 (Panorama Estrategico) e Etapa 3 (Documentos).",
                    }
                ],
            },
        ]

        response2 = client.messages.create(
            model=params["model"],
            max_tokens=params["max_tokens"],
            system=params["system"],
            messages=continuation_messages,
            tools=params["tools"],
            tool_choice={"type": "auto"},
        )

        print(f"\n[6] Continuacao - stop_reason: {response2.stop_reason}")
        print(f"    content blocks: {len(response2.content)}")

        text_parts2 = []
        for i, block in enumerate(response2.content):
            print(f"    block[{i}]: type={block.type}", end="")
            if block.type == "text":
                print(f", len={len(block.text)} chars")
                text_parts2.append(block.text)
            else:
                print()

        full_text2 = "\n\n".join(text_parts2)
        panorama2, documentos2 = _parse_text_sections(full_text2)

        print(f"\n[7] Panorama apos continuacao: {len(panorama2)} chars")
        if panorama2:
            print(f"    Primeiros 500 chars:\n{panorama2[:500]}")
        else:
            print("    >>> PANORAMA AINDA VAZIO <<<")
            # Mostrar texto bruto para debug
            print(f"    Texto bruto ({len(full_text2)} chars):")
            print(f"    {full_text2[:1000]}")

        print(f"    Documentos apos continuacao: {len(documentos2)}")
        for d in documentos2:
            print(f"      - {d.tipo}: {len(d.conteudo_markdown)} chars")

    print(f"\n{'='*70}\n")
    return response.stop_reason, len(panorama), len(full_text)


if __name__ == "__main__":
    results = []

    # Rodar apenas 1 teste se quiser economizar tokens
    if "--all" in sys.argv:
        tests = [
            (BRIEFING_CONSUMIDOR, "Consumidor - Produto com defeito"),
            (BRIEFING_MARCAS, "Marcas - Violacao de marca registrada"),
            (BRIEFING_FAMILIA, "Familia - Divorcio consensual"),
        ]
    else:
        tests = [(BRIEFING_CONSUMIDOR, "Consumidor - Produto com defeito")]

    for briefing, label in tests:
        stop, pan_len, text_len = run_test(briefing, label)
        results.append((label, stop, pan_len, text_len))

    print("\n" + "="*70)
    print("RESUMO")
    print("="*70)
    for label, stop, pan_len, text_len in results:
        status = "OK" if pan_len > 0 else "VAZIO"
        print(f"  {label}: stop={stop}, panorama={pan_len} chars [{status}], texto={text_len} chars")

    # Diagnóstico
    all_empty = all(r[2] == 0 for r in results)
    all_tool_use = all(r[1] == "tool_use" for r in results)

    if all_empty and all_tool_use:
        print("\n>>> DIAGNOSTICO: Confirmado! Claude para no tool_use.")
        print("    FIX: Enviar tool_result e continuar a conversa para obter Etapas 2 e 3.")
    elif all_empty:
        print("\n>>> DIAGNOSTICO: Panorama vazio mas stop_reason != tool_use.")
        print("    Verificar regex de parsing em _parse_text_sections().")
    else:
        print("\n>>> DIAGNOSTICO: Panorama NAO esta vazio. Problema pode ser no salvamento no DB.")
