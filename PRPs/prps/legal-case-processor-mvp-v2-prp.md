# PRP: Legal Case Processor MVP v2 — Escritório Raphael

**Gerado em:** 2026-03-04
**Confidence Score:** 8.5/10
**Origem:** projeto-raphael-planejamento.md + prompt-legal-case-processor.md + transcricao-audio
**Revisão adversarial:** 5 fases (hacker, red-team, efficiency, linguist, LLM-reception)

---

## 1. Core (OBRIGATÓRIO)

### Goal
Aplicação Python CLI que recebe briefing jurídico informal → chama Claude API (1 chamada) → entrega: ficha estruturada JSON + panorama estratégico + documentos DOCX prontos (procuração, contrato de honorários).

### Why
Raphael é advogado solo. Casos pequenos de parceiro de marcas/patentes/franchising tomam tempo desproporcional. Ele quer jogar o briefing e voltar depois para o resultado pronto. Hoje usa ChatGPT manualmente — muita interação, pouca automação.

### What
1. CLI aceita briefing (arquivo, texto inline, stdin)
2. **1 chamada** à Claude API com system prompt de 3 etapas (Ficha → Panorama → Documentos)
3. Ficha do caso extraída via **tool_use** (JSON estruturado, sem regex)
4. Panorama e documentos mantidos como texto livre (markdown)
5. Procuração e contrato gerados como DOCX via docxtpl
6. Tudo salvo em `output/{caso_id}/`

### Success Criteria
- [ ] Briefing entra como texto informal → output completo sai sem intervenção humana
- [ ] Ficha do caso em JSON válido (via tool_use, não parsing de markdown)
- [ ] Procuração ad judicia como DOCX com dados reais preenchidos
- [ ] Contrato de honorários como DOCX com dados reais preenchidos
- [ ] Dados ausentes marcados `⚠️ PENDENTE` (nunca inventados)
- [ ] Citações legais marcadas `[VERIFICAR]`
- [ ] Caso complexo emite `🔴 CASO COMPLEXO`
- [ ] 4 fixtures passam: marcas, consumidor, empresarial, input mínimo

---

## 2. Context

### Decisões Arquiteturais (FINAIS — não rediscutir)

**D1. Uma chamada API, não três.**
O system prompt produz 3 seções em 1 resposta. Não há orquestração multi-agente no MVP. O prompt já existe e foi validado: `insumos/prompt-legal-case-processor.md`.

**D2. Hybrid output: tool_use (ficha) + texto livre (resto).**
A ficha do caso é parseada via `tool_use` do Claude — o modelo preenche um schema JSON definido como tool. O panorama estratégico e os documentos são retornados como texto markdown (são para leitura humana, não para parsing). Isso elimina o risco #1 do PRP v1: parsing de markdown com regex.

**D3. DOCX via docxtpl, não geração from-scratch.**
Templates DOCX são criados uma vez via script Python (python-docx). Depois, docxtpl renderiza os templates com dados do caso. O Claude NÃO gera o DOCX — ele gera os dados, o código monta o documento.

**D4. CLI como package executável.**
Estrutura: `raphael_legal/` (package) com `__main__.py`. Executar via `python -m raphael_legal processar --arquivo caso.txt`.

**D5. Inputs do mundo real são caóticos.**
Transcrições de WhatsApp, texto fragmentado, dados parciais. O sistema NUNCA rejeita input — processa o que tem, sinaliza o que falta.

### Referência: Prompt já validado
O system prompt completo está em `insumos/prompt-legal-case-processor.md` (1.200 tokens, confidence 8/10). A análise de vulnerabilidades está em `insumos/prompt-legal-case-processor-analysis.md`. **O implementador DEVE ler ambos os arquivos antes de começar.**

### Libs e Docs
- `anthropic` (Python SDK) — messages API com tool_use
- `docxtpl` — renderiza templates DOCX com Jinja2
- `python-docx` — cria templates DOCX programaticamente
- `pydantic` — models e validação

---

## 3. Tree Structure

### After (Desired)
```
raphael/
├── insumos/                                # (existente — NÃO tocar)
├── PRPs/prps/                              # (este PRP)
├── raphael_legal/                          # Package principal
│   ├── __init__.py
│   ├── __main__.py                         # Entrypoint: python -m raphael_legal
│   ├── cli.py                              # Parsing de args (argparse)
│   ├── processor.py                        # Chama Claude API, retorna CaseOutput
│   ├── prompts.py                          # System prompt + tool schema
│   ├── document_generator.py               # Renderiza DOCX com docxtpl
│   ├── models.py                           # Pydantic models
│   └── config.py                           # Settings (env vars, paths)
├── templates/
│   ├── create_templates.py                 # Script one-off para gerar os .docx
│   ├── procuracao_ad_judicia.docx          # Gerado por create_templates.py
│   └── contrato_honorarios.docx            # Gerado por create_templates.py
├── output/                                 # Gerado em runtime (no .gitignore)
│   └── {caso_id}/
│       ├── ficha.json
│       ├── panorama.md
│       ├── procuracao.docx
│       ├── contrato_honorarios.docx
│       └── output_completo.md
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_processor.py
│   ├── test_document_generator.py
│   ├── test_cli.py
│   └── fixtures/
│       ├── briefing_marcas.txt             # Registro de marca, dados parciais
│       ├── briefing_consumidor.txt         # Produto defeituoso, transcrição informal
│       ├── briefing_empresarial.txt        # Dissolução sociedade, caso complexo
│       ├── briefing_minimal.txt            # Quase sem dados (pior caso real)
│       └── claude_response_marcas.json     # Output mockado do Claude para testes
├── pyproject.toml
├── .env.example
└── .gitignore
```

---

## 4. Known Gotchas

| # | Gotcha | Solução | Criticidade |
|---|--------|---------|-------------|
| 1 | Claude pode não usar a tool corretamente (retorna texto em vez de tool_use) | Detectar: se response não tem tool_use block, fallback para parsing regex do markdown. Logar warning. | ALTA |
| 2 | Dados com acentos (ã, é, ç) em templates DOCX Jinja2 | Testar com nomes acentuados nas fixtures. docxtpl suporta Unicode nativamente. | MÉDIA |
| 3 | Campo `materia` do Claude não bate com enum | Normalizar: strip, lowercase, mapeamento fuzzy (ex: "marca" → "Marcas"). Fallback: "Outro" | MÉDIA |
| 4 | Briefing minimal (só "quer registrar marca") | Sistema processa e marca quase tudo como PENDENTE. Teste obrigatório com fixture minimal | MÉDIA |
| 5 | API timeout/erro 429/500 | Retry com backoff exponencial (3 tentativas, max 30s). anthropic SDK já tem retry built-in. | MÉDIA |
| 6 | Templates DOCX criados via python-docx ficam feios | create_templates.py deve definir estilos explicitamente (fonte, margem, espaçamento). Testar abrindo no LibreOffice. | BAIXA |

---

## 5. Implementation Blueprint

### 5A. Tool Schema para Claude API (CRÍTICO)

O Claude será chamado com `tools` parameter. A tool `extrair_ficha_caso` força output JSON para a ficha:

```python
TOOL_SCHEMA = {
    "name": "extrair_ficha_caso",
    "description": "Registra a ficha estruturada do caso jurídico extraída do briefing.",
    "input_schema": {
        "type": "object",
        "required": ["cliente_nome", "materia", "complexidade", "justificativa_complexidade", "resumo", "documentos_recebidos", "documentos_pendentes"],
        "properties": {
            "cliente_nome": {
                "type": "string",
                "description": "Nome completo do cliente. Se ausente, usar '⚠️ PENDENTE: nome do cliente'"
            },
            "cliente_cpf_cnpj": {
                "type": "string",
                "description": "CPF ou CNPJ do cliente. Se ausente, usar '⚠️ PENDENTE: CPF/CNPJ'"
            },
            "cliente_contato": {
                "type": "string",
                "description": "Telefone ou email do cliente. Se ausente, usar '⚠️ PENDENTE: contato'"
            },
            "cliente_endereco": {
                "type": "string",
                "description": "Endereço completo do cliente. Se ausente, usar '⚠️ PENDENTE: endereço'"
            },
            "parte_contraria_nome": {
                "type": "string",
                "description": "Nome da parte contrária. 'N/A' se não aplicável. '⚠️ PENDENTE' se deveria ter mas não foi informado."
            },
            "parte_contraria_cpf_cnpj": {
                "type": "string",
                "description": "CPF/CNPJ da parte contrária. 'N/A' se não aplicável."
            },
            "materia": {
                "type": "string",
                "enum": ["Marcas", "Patentes", "Franchising", "Consumidor", "Empresarial", "Família", "Civil", "Outro"]
            },
            "complexidade": {
                "type": "string",
                "enum": ["Simples", "Médio", "Complexo"]
            },
            "justificativa_complexidade": {
                "type": "string",
                "description": "1 frase justificando a classificação de complexidade"
            },
            "resumo": {
                "type": "string",
                "description": "Máximo 5 frases: fatos → problema → pretensão do cliente"
            },
            "documentos_recebidos": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lista de documentos fornecidos no briefing"
            },
            "documentos_pendentes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lista de documentos que faltam para prosseguir"
            },
            "alerta_complexo": {
                "type": "string",
                "description": "Preenchido APENAS se complexidade='Complexo'. Formato: '🔴 CASO COMPLEXO — Recomenda-se análise aprofundada antes de prosseguir. Considerar: [motivo]'"
            }
        }
    }
}
```

**Fluxo da chamada API:**
1. System prompt = conteúdo de `insumos/prompt-legal-case-processor.md`
2. User message = briefing do caso
3. tools = [TOOL_SCHEMA]
4. tool_choice = {"type": "auto"}
5. Claude responde com: tool_use block (ficha JSON) + text blocks (panorama + documentos)
6. Se Claude NÃO usar a tool: fallback para regex parsing do texto completo

**Nota sobre o system prompt com tool_use:**
Adicionar ao final do system prompt: `"Ao processar a Etapa 1 (Ficha do Caso), use a ferramenta extrair_ficha_caso para registrar os dados estruturados. Depois continue com as Etapas 2 e 3 como texto."`

### 5B. Pydantic Models

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from datetime import datetime
import uuid

class MateriaJuridica(str, Enum):
    MARCAS = "Marcas"
    PATENTES = "Patentes"
    FRANCHISING = "Franchising"
    CONSUMIDOR = "Consumidor"
    EMPRESARIAL = "Empresarial"
    FAMILIA = "Família"
    CIVIL = "Civil"
    OUTRO = "Outro"

class Complexidade(str, Enum):
    SIMPLES = "Simples"
    MEDIO = "Médio"
    COMPLEXO = "Complexo"

class ParteProcessual(BaseModel):
    nome: str = "⚠️ PENDENTE: nome"
    cpf_cnpj: str = "⚠️ PENDENTE: CPF/CNPJ"
    contato: str = "⚠️ PENDENTE: contato"
    endereco: str = "⚠️ PENDENTE: endereço"

class FichaCaso(BaseModel):
    caso_id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d") + "-" + uuid.uuid4().hex[:6])
    data_criacao: datetime = Field(default_factory=datetime.now)
    cliente: ParteProcessual
    parte_contraria: Optional[ParteProcessual] = None
    materia: MateriaJuridica
    complexidade: Complexidade
    justificativa_complexidade: str
    resumo: str
    documentos_recebidos: list[str] = []
    documentos_pendentes: list[str] = []
    alerta_complexo: Optional[str] = None

class DocumentoGerado(BaseModel):
    tipo: str  # "procuracao_ad_judicia", "contrato_honorarios", "notificacao", "peticao"
    conteudo_markdown: str  # Texto do documento como veio do Claude
    arquivo_docx: Optional[str] = None  # Path do DOCX gerado (preenchido após geração)

class CaseOutput(BaseModel):
    ficha: FichaCaso
    panorama_md: str  # Seção 2 inteira como markdown (para leitura humana)
    documentos: list[DocumentoGerado]
    output_completo_md: str  # Response inteira do Claude
```

### 5C. Template DOCX Variables

**Procuração Ad Judicia** — variáveis docxtpl:
```
{{ cliente_nome }}, {{ cliente_nacionalidade }}, {{ cliente_estado_civil }},
{{ cliente_profissao }}, {{ cliente_rg }}, {{ cliente_cpf }},
{{ cliente_endereco }}, {{ advogado_nome }}, {{ advogado_oab }},
{{ poderes }}, {{ cidade }}, {{ data_extenso }}
```

**Contrato de Honorários** — variáveis docxtpl:
```
{{ cliente_nome }}, {{ cliente_cpf_cnpj }}, {{ cliente_endereco }},
{{ advogado_nome }}, {{ advogado_oab }}, {{ objeto_contrato }},
{{ honorarios }}, {{ vigencia }}, {{ foro }}, {{ cidade }}, {{ data_extenso }}
```

Onde dado está ausente: `"_________________ [PREENCHER: {campo}]"`

---

## 6. Tasks

> Executar em ordem. Dependências implícitas: cada task pode importar módulos das tasks anteriores.

### Task 1: Scaffold do projeto
**Keywords:** create package structure, wire dependencies
**Files:** `pyproject.toml`, `raphael_legal/__init__.py`, `raphael_legal/__main__.py`, `raphael_legal/config.py`, `.env.example`, `.gitignore`, `tests/__init__.py`

**Description:**
- Package `raphael_legal` (não `src`). `__main__.py` com `from raphael_legal.cli import main; main()`.
- pyproject.toml: Python >=3.11, deps: `anthropic>=0.40`, `python-docx>=1.0`, `docxtpl>=0.18`, `pydantic>=2.0`, `python-dotenv>=1.0`. Dev deps: `pytest>=8.0`.
- config.py: classe Settings com `ANTHROPIC_API_KEY` (obrigatório), `MODEL_NAME` (default: `claude-sonnet-4-6`), `OUTPUT_DIR` (default: `./output`), `TEMPLATES_DIR` (default: `./templates`). Carregar de .env via python-dotenv.
- .gitignore: output/, .env, __pycache__, *.pyc
- .env.example: `ANTHROPIC_API_KEY=sk-ant-...`

**Validation:**
```bash
python -c "from raphael_legal.config import Settings; s = Settings(); print(s.MODEL_NAME)"
```

---

### Task 2: Pydantic models
**Keywords:** create models from blueprint 5B
**Files:** `raphael_legal/models.py`, `tests/test_models.py`

**Description:**
Implementar exatamente os models da Seção 5B. Testes:
- FichaCaso gera caso_id automaticamente no formato `YYYYMMDD-XXXXXX`
- ParteProcessual defaults são strings `⚠️ PENDENTE: ...`
- MateriaJuridica e Complexidade são enums string
- CaseOutput serializa/deserializa JSON roundtrip

**Validation:**
```bash
python -m pytest tests/test_models.py -v
```

---

### Task 3: System prompt + tool schema
**Keywords:** create prompts module with tool_use schema from blueprint 5A
**Files:** `raphael_legal/prompts.py`

**Description:**
- Constante `SYSTEM_PROMPT`: carregar conteúdo de `insumos/prompt-legal-case-processor.md` em runtime (Path(__file__).parent.parent / "insumos" / "prompt-legal-case-processor.md"). Se arquivo não existe, usar string hardcoded como fallback.
- Adicionar ao final do system prompt: instrução para usar tool `extrair_ficha_caso` na Etapa 1.
- Constante `FICHA_TOOL_SCHEMA`: dict conforme Seção 5A.
- Função `build_api_params(briefing: str) -> dict`: retorna dict com `model`, `max_tokens`, `system`, `messages`, `tools`, `tool_choice` pronto para `client.messages.create(**params)`.

**Validation:**
```bash
python -c "from raphael_legal.prompts import build_api_params; p = build_api_params('teste'); print(p.keys())"
```

---

### Task 4: Processador (Claude API + parsing)
**Keywords:** create processor, wire Claude API, extract tool_use + text
**Files:** `raphael_legal/processor.py`, `tests/test_processor.py`, `tests/fixtures/claude_response_marcas.json`

**Description:**
Classe `CaseProcessor(api_key: str, model: str)`:

Método principal `process(briefing: str) -> CaseOutput`:
1. Chamar `client.messages.create(**build_api_params(briefing))`
2. Iterar `response.content` blocks:
   - Se `block.type == "tool_use"` e `block.name == "extrair_ficha_caso"`: extrair `block.input` → criar `FichaCaso` via Pydantic
   - Se `block.type == "text"`: acumular texto
3. Do texto acumulado, separar panorama e documentos por headers markdown (`## 2.` e `## 3.`)
4. Para cada sub-header de documento (`### 3A.`, `### 3B.`, etc.): criar `DocumentoGerado`
5. Retornar `CaseOutput`

**Fallback (se Claude não usar tool_use):**
- Logar warning: "Claude não usou tool_use, tentando regex fallback"
- Extrair ficha do texto com regex (pattern: entre `## 1. FICHA` e `## 2. PANORAMA`)
- Popular FichaCaso com defaults PENDENTE para campos não extraídos

**Fixture de teste:**
Criar `tests/fixtures/claude_response_marcas.json` com response mockada que inclui tool_use block + text blocks. Usar esta fixture nos testes unitários (mock do anthropic client).

**Testes:**
- Parsing de response com tool_use: extrai ficha, panorama, documentos
- Parsing de response SEM tool_use (fallback): funciona com degradação graciosa
- Briefing vazio: retorna ficha com todos os campos PENDENTE, não crasheia
- Erro de API (mock 429): retry funciona, após 3 falhas levanta exceção clara

**Validation:**
```bash
python -m pytest tests/test_processor.py -v
```

---

### Task 5: Script de criação de templates DOCX
**Keywords:** create template generator script, wire python-docx
**Files:** `templates/create_templates.py`

**Description:**
Script executável que gera `procuracao_ad_judicia.docx` e `contrato_honorarios.docx` usando python-docx.

**Procuração:**
- Página: A4, margens 3cm (sup/esq) e 2cm (inf/dir) — padrão ABNT
- Título: "PROCURAÇÃO AD JUDICIA" centralizado, negrito, Times New Roman 14pt
- Corpo: Times New Roman 12pt, espaçamento 1.5
- Texto com placeholders Jinja2: `{{ cliente_nome }}` etc. conforme Seção 5C
- Poderes: cláusula padrão ad judicia (Art. 105 CPC) em texto fixo
- Local/data e linha de assinatura no final

**Contrato:**
- Mesma formatação base
- Título: "CONTRATO DE PRESTAÇÃO DE SERVIÇOS ADVOCATÍCIOS"
- 8 cláusulas numeradas conforme blueprint original (DAS PARTES, DO OBJETO, DOS HONORÁRIOS, DAS DESPESAS, DA VIGÊNCIA, DA RESCISÃO, DO SIGILO, DO FORO)
- Placeholders Jinja2 nos campos variáveis
- Espaço para 2 testemunhas no final

**Executar com:**
```bash
python templates/create_templates.py
```

Script deve ser idempotente (re-executar sobrescreve os .docx).

**Validation:**
```bash
python templates/create_templates.py && python -c "from docxtpl import DocxTemplate; DocxTemplate('templates/procuracao_ad_judicia.docx'); DocxTemplate('templates/contrato_honorarios.docx'); print('OK')"
```

---

### Task 6: Gerador de documentos DOCX
**Keywords:** create document generator, wire docxtpl with CaseOutput data
**Files:** `raphael_legal/document_generator.py`, `tests/test_document_generator.py`

**Description:**
Classe `DocumentGenerator(templates_dir: Path)`:

Método `generate(case_output: CaseOutput, output_dir: Path) -> list[Path]`:
1. Criar `output_dir` se não existe
2. Preparar contexto da procuração: mapear `case_output.ficha.cliente.*` para variáveis do template. Campos com `⚠️ PENDENTE` → `"_________________ [PREENCHER: {campo}]"`
3. Renderizar `procuracao_ad_judicia.docx` → salvar em `output_dir/procuracao.docx`
4. Preparar contexto do contrato: idem + extrair objeto do `case_output.ficha.resumo`
5. Renderizar `contrato_honorarios.docx` → salvar em `output_dir/contrato_honorarios.docx`
6. Retornar lista de Paths gerados

**Contexto fixo (configurável via config, defaults razoáveis):**
- `advogado_nome`: `"[PREENCHER: nome do advogado]"`
- `advogado_oab`: `"[PREENCHER: OAB nº]"`
- `honorarios`: `"[PREENCHER: valor e forma de pagamento dos honorários]"`
- `data_extenso`: data atual por extenso em português

**Testes (mock de CaseOutput, sem chamar Claude):**
- Gera procuração DOCX válida com dados completos
- Gera procuração com campos PENDENTE → aparecem como placeholder no DOCX
- Gera contrato DOCX válido
- Output dir é criado automaticamente

**Validation:**
```bash
python -m pytest tests/test_document_generator.py -v
```

---

### Task 7: CLI
**Keywords:** create CLI, wire all modules end-to-end
**Files:** `raphael_legal/cli.py`, `raphael_legal/__main__.py`, `tests/test_cli.py`

**Description:**
`cli.py` com função `main()` usando argparse:

```
python -m raphael_legal processar --arquivo briefing.txt
python -m raphael_legal processar --texto "Cliente quer registrar marca..."
cat briefing.txt | python -m raphael_legal processar --stdin
```

Fluxo de `processar`:
1. Ler briefing de --arquivo, --texto, ou --stdin (exatamente 1 obrigatório)
2. Validar: briefing não vazio, API key configurada
3. `CaseProcessor.process(briefing)` → CaseOutput
4. Salvar ficha.json, panorama.md, output_completo.md em `output/{caso_id}/`
5. `DocumentGenerator.generate(case_output, output_dir)` → DOCX files
6. Imprimir resumo:
   ```
   Caso processado: {caso_id}
   Matéria: {materia} | Complexidade: {complexidade}
   {alerta_complexo se houver}
   Documentos:
     output/{caso_id}/ficha.json
     output/{caso_id}/panorama.md
     output/{caso_id}/procuracao.docx
     output/{caso_id}/contrato_honorarios.docx
   ```

**Erro handling:**
- API key ausente → mensagem clara: "Configure ANTHROPIC_API_KEY em .env"
- Arquivo não encontrado → mensagem clara
- Erro de API → mensagem com status code, sem stacktrace para o usuário

**Testes:**
- --arquivo com fixture existente (mock API)
- --stdin com pipe (mock API)
- --arquivo inexistente → erro amigável
- Sem API key → erro amigável

**Validation:**
```bash
python -m pytest tests/test_cli.py -v
```

---

### Task 8: Fixtures de teste realistas
**Keywords:** create realistic test fixtures in Brazilian Portuguese
**Files:** `tests/fixtures/briefing_marcas.txt`, `tests/fixtures/briefing_consumidor.txt`, `tests/fixtures/briefing_empresarial.txt`, `tests/fixtures/briefing_minimal.txt`, `tests/fixtures/claude_response_marcas.json`

**Description:**

**briefing_marcas.txt** — Registro de marca (dados parciais):
```
Oi Raphael, segue o caso novo. O João Silva da JS Alimentos quer registrar
a marca "Café Premium" no INPI, classe 30. CNPJ da empresa: 12.345.678/0001-90.
Endereço da empresa: Rua das Flores, 123, São Paulo/SP. CEP 01234-000.
Ele já fez busca prévia e não encontrou marca similar. Quer saber os passos
e custos. Segue o comprovante de CNPJ em anexo.
```

**briefing_consumidor.txt** — Transcrição informal de áudio:
```
Então, a dona Maria comprou uma geladeira na Magazine Luiza, modelo Brastemp
BRM44, pagou R$ 3.200,00 no cartão. Chegou com defeito, não gela direito.
Já chamou a assistência duas vezes, não resolveu. Faz 45 dias que comprou.
Quer trocar ou devolver. CPF dela: 987.654.321-00. Mora em Campinas/SP,
Rua dos Lírios, 456. Telefone: (19) 99876-5432.
```

**briefing_empresarial.txt** — Caso complexo:
```
Raphael, caso complicado aqui. Três sócios numa LTDA (Empresa ABC Tecnologia LTDA,
CNPJ 11.222.333/0001-44). Sócio A (60%) quer sair, sócios B (25%) e C (15%)
querem continuar. Tem divergência sobre valuation da empresa. Contrato social
não prevê cláusula de saída. Empresa fatura R$ 2M/ano. Tem imóvel no ativo.
Sócio A quer dissolução parcial. Não tem acordo sobre apuração de haveres.
```

**briefing_minimal.txt** — Pior caso real:
```
quer registrar uma marca
```

**claude_response_marcas.json** — Mock de response do Claude com tool_use para o caso de marcas. Deve conter:
- 1 tool_use block com name="extrair_ficha_caso" e input com dados do briefing_marcas
- 1+ text blocks com panorama estratégico (via administrativa INPI + via judicial se oposição) e documentos (procuração + contrato)
- Marcadores [VERIFICAR] em fundamentos legais
- Formato realista de como Claude realmente responde

**Validation:**
```bash
python -c "import json; json.load(open('tests/fixtures/claude_response_marcas.json')); print('OK')"
```

---

### Task 9: Teste de integração end-to-end (com mock)
**Keywords:** wire end-to-end test, mock Claude API, verify full pipeline
**Files:** `tests/test_integration.py`

**Description:**
Teste que executa o pipeline completo com API mockada:
1. Ler cada fixture de briefing
2. Mock do anthropic client retorna fixture `claude_response_marcas.json` (ou variante)
3. Verificar: ficha.json gerado e válido, panorama.md não vazio, DOCX files existem e têm tamanho > 0
4. Verificar: nenhum dado inventado (CPF no output deve existir no input ou ser PENDENTE)
5. Para briefing_minimal: verificar que maioria dos campos é PENDENTE

**Validation:**
```bash
python -m pytest tests/test_integration.py -v
```

---

## 7. Validation Gating

### Level 1: Compilação
```bash
python -m py_compile raphael_legal/models.py && \
python -m py_compile raphael_legal/prompts.py && \
python -m py_compile raphael_legal/processor.py && \
python -m py_compile raphael_legal/document_generator.py && \
python -m py_compile raphael_legal/cli.py && \
echo "Level 1: OK"
```

### Level 2: Testes unitários + integração (mock)
```bash
python -m pytest tests/ -v --tb=short
```
**Critério:** All pass. Se algum falhar, corrigir antes de prosseguir.

### Level 3: Teste real com Claude API (requer ANTHROPIC_API_KEY)
```bash
echo "João Silva, CPF 123.456.789-00, quer registrar marca Café Premium no INPI. CNPJ 12.345.678/0001-90. São Paulo/SP." | python -m raphael_legal processar --stdin
```
**Verificar manualmente:**
- [ ] ficha.json: matéria=Marcas, CPF correto, nenhum dado inventado
- [ ] panorama.md: ao menos 1 via estratégica, tem [VERIFICAR]
- [ ] procuracao.docx: abre no Word/LibreOffice, dados preenchidos
- [ ] contrato_honorarios.docx: abre, honorários como [PREENCHER]

### Level 4: Smoke test multi-matéria
```bash
for f in tests/fixtures/briefing_*.txt; do
  echo "=== $f ===" && python -m raphael_legal processar --arquivo "$f"
done
```
**Critério:** Todos processam sem crash. Matéria classificada coerentemente.

---

## 8. Confidence Assessment

**Score:** 8.5/10

**Melhorias vs v1 (+1.5):**
- [+0.5] tool_use elimina fragilidade de parsing regex para ficha
- [+0.3] Fixture de response mockada permite testes sem API
- [+0.2] Package structure correta (__main__.py, não src.main)
- [+0.2] Script dedicado para templates DOCX (não handwaved)
- [+0.2] Fixture minimal testa pior caso real
- [+0.1] Fallback explícito se tool_use falhar

**Riscos remanescentes:**
- [-0.5] Templates DOCX genéricos (não os do Raphael). Mitigação: fácil substituir depois.
- [-0.5] Sem few-shot example no prompt. Mitigação: prompt já tem confidence 8/10 sem ele.
- [-0.5] Parsing de panorama/documentos ainda é regex (mas é texto para humanos, tolerância maior)

---

*PRP v2 generated by adversarial review (5 phases)*
*IMPORTANTE: Execute em nova instância do Claude Code (use /clear antes de executar)*
*Executar: /dev-kit:11-execute-prp PRPs/prps/legal-case-processor-mvp-v2-prp.md*
