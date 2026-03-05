import argparse
import json
import sys
from pathlib import Path

from raphael_legal.config import Settings
from raphael_legal.document_generator import DocumentGenerator
from raphael_legal.processor import CaseProcessor


def _read_briefing(args: argparse.Namespace) -> str:
    if args.arquivo:
        path = Path(args.arquivo)
        if not path.exists():
            print(f"Erro: arquivo não encontrado: {args.arquivo}", file=sys.stderr)
            sys.exit(1)
        return path.read_text(encoding="utf-8")
    elif args.texto:
        return args.texto
    elif args.stdin:
        return sys.stdin.read()
    else:
        print("Erro: forneça --arquivo, --texto ou --stdin", file=sys.stderr)
        sys.exit(1)


def _cmd_processar(args: argparse.Namespace) -> None:
    settings = Settings()

    if not settings.ANTHROPIC_API_KEY:
        print("Erro: Configure ANTHROPIC_API_KEY em .env", file=sys.stderr)
        sys.exit(1)

    briefing = _read_briefing(args)
    if not briefing.strip():
        print("Erro: briefing vazio", file=sys.stderr)
        sys.exit(1)

    try:
        processor = CaseProcessor(
            api_key=settings.ANTHROPIC_API_KEY,
            model=settings.MODEL_NAME,
        )
        result = processor.process(briefing)
    except Exception as e:
        print(f"Erro ao processar caso: {e}", file=sys.stderr)
        sys.exit(1)

    # Save outputs
    caso_id = result.ficha.caso_id
    output_dir = settings.OUTPUT_DIR / caso_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # ficha.json
    ficha_path = output_dir / "ficha.json"
    ficha_path.write_text(
        result.ficha.model_dump_json(indent=2),
        encoding="utf-8",
    )

    # panorama.md
    panorama_path = output_dir / "panorama.md"
    panorama_path.write_text(result.panorama_md, encoding="utf-8")

    # output_completo.md
    completo_path = output_dir / "output_completo.md"
    completo_path.write_text(result.output_completo_md, encoding="utf-8")

    # DOCX documents
    try:
        doc_gen = DocumentGenerator(settings.TEMPLATES_DIR)
        doc_gen.generate(result, output_dir)
    except Exception as e:
        print(f"Aviso: erro ao gerar DOCX: {e}", file=sys.stderr)

    # Print summary
    print(f"\nCaso processado: {caso_id}")
    print(f"Matéria: {result.ficha.materia.value} | Complexidade: {result.ficha.complexidade.value}")
    if result.ficha.alerta_complexo:
        print(result.ficha.alerta_complexo)
    print("Documentos:")
    for f in sorted(output_dir.iterdir()):
        print(f"  {f}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="raphael_legal",
        description="Processador de casos jurídicos",
    )
    subparsers = parser.add_subparsers(dest="comando")

    proc = subparsers.add_parser("processar", help="Processar um caso jurídico")
    group = proc.add_mutually_exclusive_group(required=True)
    group.add_argument("--arquivo", help="Caminho do arquivo com o briefing")
    group.add_argument("--texto", help="Texto do briefing inline")
    group.add_argument("--stdin", action="store_true", help="Ler briefing do stdin")

    args = parser.parse_args()

    if args.comando == "processar":
        _cmd_processar(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
