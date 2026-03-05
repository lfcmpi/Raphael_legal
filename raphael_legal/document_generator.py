import locale
from datetime import datetime
from pathlib import Path

from docxtpl import DocxTemplate

from raphael_legal.models import CaseOutput

_PENDENTE_MARKER = "⚠️ PENDENTE"
_PLACEHOLDER_FMT = "_________________ [PREENCHER: {campo}]"

_MESES_PT = [
    "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def _data_extenso() -> str:
    now = datetime.now()
    return f"{now.day} de {_MESES_PT[now.month]} de {now.year}"


def _val_or_placeholder(valor: str, campo: str) -> str:
    if _PENDENTE_MARKER in valor:
        return _PLACEHOLDER_FMT.format(campo=campo)
    return valor


class DocumentGenerator:
    def __init__(self, templates_dir: Path) -> None:
        self._templates_dir = templates_dir

    def generate(self, case_output: CaseOutput, output_dir: Path) -> list[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        generated: list[Path] = []

        generated.append(self._generate_procuracao(case_output, output_dir))
        generated.append(self._generate_contrato(case_output, output_dir))

        return generated

    def _generate_procuracao(self, case_output: CaseOutput, output_dir: Path) -> Path:
        tpl_path = self._templates_dir / "procuracao_ad_judicia.docx"
        doc = DocxTemplate(str(tpl_path))

        cliente = case_output.ficha.cliente
        context = {
            "cliente_nome": _val_or_placeholder(cliente.nome, "nome do cliente"),
            "cliente_nacionalidade": _PLACEHOLDER_FMT.format(campo="nacionalidade"),
            "cliente_estado_civil": _PLACEHOLDER_FMT.format(campo="estado civil"),
            "cliente_profissao": _PLACEHOLDER_FMT.format(campo="profissão"),
            "cliente_rg": _PLACEHOLDER_FMT.format(campo="RG"),
            "cliente_cpf": _val_or_placeholder(cliente.cpf_cnpj, "CPF/CNPJ"),
            "cliente_endereco": _val_or_placeholder(cliente.endereco, "endereço"),
            "advogado_nome": "[PREENCHER: nome do advogado]",
            "advogado_oab": "[PREENCHER: OAB nº]",
            "advogado_endereco": "[PREENCHER: endereço do escritório]",
            "poderes": "inclusive os da cláusula ad judicia",
            "cidade": "[PREENCHER: cidade]",
            "data_extenso": _data_extenso(),
        }

        doc.render(context)
        out_path = output_dir / "procuracao.docx"
        doc.save(str(out_path))
        return out_path

    def _generate_contrato(self, case_output: CaseOutput, output_dir: Path) -> Path:
        tpl_path = self._templates_dir / "contrato_honorarios.docx"
        doc = DocxTemplate(str(tpl_path))

        cliente = case_output.ficha.cliente
        resumo = case_output.ficha.resumo

        context = {
            "cliente_nome": _val_or_placeholder(cliente.nome, "nome do cliente"),
            "cliente_cpf_cnpj": _val_or_placeholder(cliente.cpf_cnpj, "CPF/CNPJ"),
            "cliente_endereco": _val_or_placeholder(cliente.endereco, "endereço"),
            "advogado_nome": "[PREENCHER: nome do advogado]",
            "advogado_oab": "[PREENCHER: OAB nº]",
            "advogado_endereco": "[PREENCHER: endereço do escritório]",
            "objeto_contrato": resumo if _PENDENTE_MARKER not in resumo else _PLACEHOLDER_FMT.format(campo="objeto do contrato"),
            "honorarios": "[PREENCHER: valor e forma de pagamento dos honorários]",
            "vigencia": "até a conclusão definitiva do processo objeto deste contrato",
            "foro": "[PREENCHER: comarca]",
            "cidade": "[PREENCHER: cidade]",
            "data_extenso": _data_extenso(),
        }

        doc.render(context)
        out_path = output_dir / "contrato_honorarios.docx"
        doc.save(str(out_path))
        return out_path
