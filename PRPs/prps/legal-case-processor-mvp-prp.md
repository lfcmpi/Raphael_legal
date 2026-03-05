# PRP: Legal Case Processor MVP — Escritório Raphael

**Gerado em:** 2026-03-04
**Confidence Score:** 7/10
**Origem:** projeto-raphael-planejamento.md + prompt-legal-case-processor.md + transcricao-audio

---

## 1. Core (OBRIGATÓRIO)

### Goal
Construir um processador de casos jurídicos que recebe briefings informais e entrega ficha estruturada + panorama estratégico + documentos prontos (procuração, contrato de honorários), usando Claude API como LLM.

### Why
Raphael é advogado solo que perde tempo desproporcional em casos pequenos enviados por parceiro de marcas/patentes/franchising. Hoje usa ChatGPT/Gemini manualmente, o que exige muita interação. O sistema deve processar casos **assincronamente** — ele joga o briefing e volta quando o resultado estiver pronto.

### What
Aplicação Python (CLI + API) que:
1. Recebe briefing de caso (texto livre, transcrição de áudio, dados fragmentados)
2. Processa em 3 etapas via Claude API (Ficha → Panorama Estratégico → Documentos)
3. Gera documentos formatados em DOCX (procuração ad judicia, contrato de honorários)
4. Salva output estruturado (JSON + DOCX) em diretório organizado por caso

### Success Criteria
- [ ] CLI aceita briefing como texto (stdin, arquivo .txt/.md, ou argumento)
- [ ] Processamento gera output completo em 3 etapas (ficha + panorama + documentos)
- [ ] Procuração ad judicia gerada como DOCX formatado usando template
- [ ] Contrato de honorários gerado como DOCX formatado usando template
- [ ] Output JSON estruturado com ficha do caso extraída
- [ ] Campos pendentes marcados com `⚠️ PENDENTE` (não inventa dados)
- [ ] Citações legais marcadas com `[VERIFICAR]`
- [ ] Casos complexos emitem alerta `🔴 CASO COMPLEXO`
- [ ] Testes passam para cenários de marcas, consumidor e empresarial

---

## 2. Context

### Codebase Analysis
```
Projeto greenfield — sem código existente.
Diretório atual contém apenas insumos de planejamento:
- projeto-raphael-planejamento.md (arquitetura de 5 agentes)
- prompt-legal-case-processor.md (prompt otimizado em 3 etapas)
- prompt-legal-case-processor-analysis.md (análise de vulnerabilidades)
- transcricao-audio-2026-03-04.md (requisitos do Raphael)
```

### Decisões de Arquitetura Já Tomadas
```
1. Pipeline de 5 agentes consolidado em 3 etapas (conforme analysis.md):
   - Etapa 1: Ficha do Caso (intake + classificação + gaps)
   - Etapa 2: Panorama Estratégico (vias administrativa/extrajudicial/judicial)
   - Etapa 3: Documentos (procuração, contrato, notificação se aplicável)

2. Prompt único com 3 etapas (não multi-agente no MVP):
   - Mais simples de implementar e debugar
   - Sem overhead de orquestração entre agentes
   - Suficiente para MVP baseado no volume atual

3. Marcadores de segurança obrigatórios:
   - [VERIFICAR] para toda citação legal
   - ⚠️ PENDENTE para dados não fornecidos
   - 🔴 CASO COMPLEXO como regra de parada
   - Proibido: honorários, probabilidades numéricas
```

### External Documentation
```
- Anthropic Python SDK: https://docs.anthropic.com/en/docs/build-with-claude/
- python-docx: https://python-docx.readthedocs.io/
- docxtpl (Jinja2 templates para DOCX): https://docxtpl.readthedocs.io/
```

---

## 3. Tree Structure

### Before (Current)
```
raphael/
└── insumos/
    ├── projeto-raphael-planejamento.md
    ├── prompt-legal-case-processor.md
    ├── prompt-legal-case-processor-analysis.md
    └── transcricao-audio-2026-03-04.md
```

### After (Desired)
```
raphael/
├── insumos/                              # (existente - não tocar)
├── PRPs/prps/                            # (este PRP)
├── src/
│   ├── __init__.py
│   ├── main.py                           # CLI entrypoint
│   ├── processor.py                      # Orquestra as 3 etapas via Claude API
│   ├── prompts.py                        # System prompt + formatação de user prompt
│   ├── document_generator.py             # Gera DOCX a partir do output do Claude
│   ├── models.py                         # Pydantic models (CaseFile, Strategy, etc.)
│   └── config.py                         # Configurações (API key, paths, etc.)
├── templates/
│   ├── procuracao_ad_judicia.docx        # Template DOCX com placeholders Jinja2
│   └── contrato_honorarios.docx          # Template DOCX com placeholders Jinja2
├── output/                               # Diretório de saída (gerado em runtime)
│   └── {caso_id}/                        # Subdiretório por caso
│       ├── ficha.json                    # Ficha estruturada
│       ├── panorama.md                   # Panorama estratégico
│       ├── procuracao.docx               # Procuração gerada
│       ├── contrato.docx                 # Contrato gerado
│       └── output_completo.md            # Output integral do Claude
├── tests/
│   ├── __init__.py
│   ├── test_processor.py                 # Testes do processador
│   ├── test_document_generator.py        # Testes de geração DOCX
│   ├── test_models.py                    # Testes dos models
│   └── fixtures/
│       ├── briefing_marcas.txt           # Briefing exemplo: registro de marca
│       ├── briefing_consumidor.txt       # Briefing exemplo: caso consumidor
│       └── briefing_empresarial.txt      # Briefing exemplo: caso empresarial
├── pyproject.toml                        # Dependências e config do projeto
├── .env.example                          # Exemplo de variáveis de ambiente
└── .gitignore
```

---

## 4. Known Gotchas

| Gotcha | Solução |
|--------|---------|
| Claude pode gerar output não-parseável (markdown irregular) | Usar structured output com Pydantic + parsing robusto com fallback para texto livre |
| Citações legais alucinadas | Marcadores `[VERIFICAR]` já no prompt; não tentar validar automaticamente no MVP |
| Input muito longo (briefing extenso + docs) | Usar Claude Sonnet para balancear custo/qualidade; input até 200k tokens suportado |
| Templates DOCX com formatação OAB | Criar templates manuais com formatação correta; docxtpl substitui apenas variáveis |
| python-docx não suporta PDF nativo | MVP entrega DOCX apenas; PDF via LibreOffice CLI ou WeasyPrint em fase futura |
| Dados sensíveis (CPF, endereço) em logs | Não logar conteúdo do briefing nem output; .gitignore no diretório output/ |
| Modelo drift para common law (~15% dos casos) | Ancoragem jurisdicional explícita no system prompt (já implementada) |
| Casos multi-matéria | MVP classifica em UMA categoria principal (decisão deliberada por simplicidade) |

---

## 5. Implementation Blueprint

### Data Models / Schemas

```python
# models.py
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime

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
    nome: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    contato: Optional[str] = None
    endereco: Optional[str] = None
    campos_pendentes: list[str] = []

class FichaCaso(BaseModel):
    caso_id: str
    data_criacao: datetime
    cliente: ParteProcessual
    parte_contraria: Optional[ParteProcessual] = None
    materia: MateriaJuridica
    complexidade: Complexidade
    justificativa_complexidade: str
    resumo: str
    documentos_recebidos: list[str]
    documentos_pendentes: list[str]
    alerta_complexo: Optional[str] = None  # Preenchido se complexidade == COMPLEXO

class ViaEstrategica(BaseModel):
    tipo: str  # "Administrativa", "Extrajudicial", "Judicial"
    acao: str
    fundamento_legal: str  # Sempre com [VERIFICAR]
    prazo_estimado: str
    custo_beneficio: str
    risco_principal: str

class PanoramaEstrategico(BaseModel):
    vias: list[ViaEstrategica]
    recomendacao_preliminar: str

class DocumentoGerado(BaseModel):
    tipo: str  # "procuracao", "contrato", "notificacao", "peticao"
    conteudo_texto: str  # Conteúdo em texto (antes de virar DOCX)
    arquivo_docx: Optional[str] = None  # Path do DOCX gerado

class CaseOutput(BaseModel):
    ficha: FichaCaso
    panorama: PanoramaEstrategico
    documentos: list[DocumentoGerado]
    output_completo_md: str  # Output integral do Claude
```

### Integration Points

| Ponto | Arquivo | Modificação |
|-------|---------|-------------|
| Entrypoint CLI | `src/main.py` | create — argparse com subcomandos |
| Claude API call | `src/processor.py` | create — messages API com system prompt |
| System prompt | `src/prompts.py` | create — prompt do prompt-legal-case-processor.md |
| Parsing de output | `src/processor.py` | create — extrair seções do markdown do Claude |
| Geração DOCX | `src/document_generator.py` | create — docxtpl com templates |
| Templates | `templates/*.docx` | create — templates DOCX com placeholders |
| Configuração | `src/config.py` | create — env vars, paths |

---

## 6. Tasks

### Task 1: Scaffold do projeto Python
**Keywords:** create project structure, wire dependencies
**Files:**
- `pyproject.toml` (create)
- `src/__init__.py` (create)
- `src/config.py` (create)
- `.env.example` (create)
- `.gitignore` (create)

**Description:**
Criar estrutura do projeto Python com pyproject.toml (usando uv ou pip). Dependências: `anthropic`, `python-docx`, `docxtpl`, `pydantic`, `python-dotenv`. Config carrega ANTHROPIC_API_KEY de .env. Usar Python 3.11+.

**Validation:**
```bash
cd src && python -c "from config import settings; print(settings)"
```

---

### Task 2: Definir Pydantic models
**Keywords:** create data models, define schemas
**Files:**
- `src/models.py` (create)

**Description:**
Implementar todos os models conforme blueprint da Seção 5. Incluir validators: caso_id gerado automaticamente (UUID ou data+sequencial), campos_pendentes populados quando valor é None.

**Validation:**
```bash
python -m pytest tests/test_models.py -v
```

---

### Task 3: Implementar módulo de prompts
**Keywords:** create prompt module, inject system prompt
**Files:**
- `src/prompts.py` (create)

**Description:**
Conter o system prompt completo de `prompt-legal-case-processor.md` como constante. Função `build_user_prompt(briefing: str) -> str` que formata o briefing do usuário. Função `build_messages(briefing: str) -> list[dict]` que retorna messages formatadas para a API do Claude.

**Validation:**
```bash
python -c "from src.prompts import build_messages; msgs = build_messages('teste'); print(len(msgs))"
```

---

### Task 4: Implementar processador principal (Claude API)
**Keywords:** create processor, wire Claude API, parse output
**Files:**
- `src/processor.py` (create)

**Description:**
Classe `CaseProcessor` que:
1. Recebe briefing (string)
2. Chama Claude API (model: claude-sonnet-4-6) com system prompt + user prompt
3. Recebe output markdown completo
4. Parseia output em 3 seções (ficha, panorama, documentos)
5. Popula Pydantic models com dados extraídos
6. Retorna `CaseOutput`

Parsing: usar regex para separar seções por headers (`## 1. FICHA DO CASO`, `## 2. PANORAMA ESTRATÉGICO`, `## 3. DOCUMENTOS`). Para a ficha, extrair campos estruturados. Para panorama e documentos, manter como texto + extrair o que for possível para os models.

Tratar edge cases: output sem uma seção (logar warning, continuar), output com formatação inesperada (salvar raw e continuar).

**Validation:**
```bash
python -m pytest tests/test_processor.py -v
```

---

### Task 5: Criar templates DOCX
**Keywords:** create DOCX templates, wire Jinja2 placeholders
**Files:**
- `templates/procuracao_ad_judicia.docx` (create)
- `templates/contrato_honorarios.docx` (create)

**Description:**
Criar templates DOCX com formatação jurídica brasileira padrão.

**Procuração Ad Judicia:**
- Título: "PROCURAÇÃO AD JUDICIA"
- Outorgante: `{{ cliente_nome }}`, `{{ cliente_nacionalidade }}`, `{{ cliente_estado_civil }}`, `{{ cliente_profissao }}`, portador(a) do RG nº `{{ cliente_rg }}` e CPF nº `{{ cliente_cpf }}`, residente e domiciliado(a) em `{{ cliente_endereco }}`
- Outorgado: `{{ advogado_nome }}`, inscrito(a) na OAB/`{{ advogado_oab_estado }}` sob nº `{{ advogado_oab_numero }}`
- Poderes: cláusula ad judicia padrão (foro geral e especial, poderes da cláusula ad judicia do Art. 105 CPC, receber e dar quitação, firmar compromisso, substabelecer com ou sem reservas)
- Local e data: `{{ cidade }}`, `{{ data_extenso }}`
- Assinatura: linha para outorgante

**Contrato de Honorários:**
- Título: "CONTRATO DE PRESTAÇÃO DE SERVIÇOS ADVOCATÍCIOS"
- Cláusula 1ª - DAS PARTES: dados do contratante e contratado
- Cláusula 2ª - DO OBJETO: `{{ objeto_contrato }}`
- Cláusula 3ª - DOS HONORÁRIOS: `{{ honorarios_descricao }}` (placeholder para Raphael preencher)
- Cláusula 4ª - DAS DESPESAS: cliente arca com custas processuais e despesas
- Cláusula 5ª - DA VIGÊNCIA: `{{ vigencia }}`
- Cláusula 6ª - DA RESCISÃO: condições de rescisão
- Cláusula 7ª - DO SIGILO: cláusula de confidencialidade (LGPD)
- Cláusula 8ª - DO FORO: `{{ foro }}`
- Assinaturas: contratante e contratado, 2 testemunhas

Templates devem usar fonte Times New Roman 12pt, margens padrão ABNT, espaçamento 1.5.

**Nota:** Templates DOCX com Jinja2 tags devem ser criados programaticamente via python-docx (criar script auxiliar) já que não podemos criar .docx binário diretamente.

**Validation:**
```bash
python -c "from docxtpl import DocxTemplate; t = DocxTemplate('templates/procuracao_ad_judicia.docx'); print('OK')"
```

---

### Task 6: Implementar gerador de documentos DOCX
**Keywords:** create document generator, wire docxtpl, extract data from output
**Files:**
- `src/document_generator.py` (create)

**Description:**
Classe `DocumentGenerator` que:
1. Recebe `CaseOutput` (do processador)
2. Mapeia dados da ficha para variáveis do template
3. Usa docxtpl para renderizar templates com dados reais
4. Onde dado está pendente, insere "_________________ [PREENCHER: campo]"
5. Salva DOCX no diretório output/{caso_id}/
6. Retorna paths dos arquivos gerados

Funções auxiliares:
- `_prepare_procuracao_context(ficha: FichaCaso) -> dict` — mapeia campos
- `_prepare_contrato_context(ficha: FichaCaso, panorama: PanoramaEstrategico) -> dict`
- `_ensure_output_dir(caso_id: str) -> Path` — cria diretório se não existe

**Validation:**
```bash
python -m pytest tests/test_document_generator.py -v
```

---

### Task 7: Implementar CLI (main.py)
**Keywords:** create CLI entrypoint, wire all modules
**Files:**
- `src/main.py` (create)

**Description:**
CLI com argparse:

```
# Processar briefing de arquivo
python -m src.main processar --arquivo briefing.txt

# Processar briefing inline
python -m src.main processar --texto "Cliente João Silva precisa registrar marca..."

# Processar de stdin (pipe)
cat briefing.txt | python -m src.main processar --stdin
```

Fluxo:
1. Ler briefing (arquivo, texto, ou stdin)
2. Instanciar `CaseProcessor` e processar
3. Salvar output completo em markdown
4. Gerar documentos DOCX via `DocumentGenerator`
5. Imprimir resumo no terminal:
   ```
   ✓ Caso processado: {caso_id}
   ✓ Matéria: {materia}
   ✓ Complexidade: {complexidade}
   ✓ Documentos gerados:
     - output/{caso_id}/procuracao.docx
     - output/{caso_id}/contrato.docx
     - output/{caso_id}/panorama.md
     - output/{caso_id}/ficha.json
   ```

**Validation:**
```bash
echo "Cliente: João Silva. Precisa registrar marca XPTO no INPI. CNPJ: 12.345.678/0001-90" | python -m src.main processar --stdin
```

---

### Task 8: Criar fixtures de teste e testes
**Keywords:** create test fixtures, create unit tests
**Files:**
- `tests/__init__.py` (create)
- `tests/test_models.py` (create)
- `tests/test_processor.py` (create)
- `tests/test_document_generator.py` (create)
- `tests/fixtures/briefing_marcas.txt` (create)
- `tests/fixtures/briefing_consumidor.txt` (create)
- `tests/fixtures/briefing_empresarial.txt` (create)

**Description:**
**Fixtures** — 3 briefings realistas em português:
1. `briefing_marcas.txt`: Cliente quer registrar marca no INPI; dados parciais (sem RG)
2. `briefing_consumidor.txt`: Cliente teve produto com defeito, quer acionar fabricante; transcrição informal de áudio
3. `briefing_empresarial.txt`: Dissolução parcial de sociedade; caso complexo

**Testes:**
- `test_models.py`: Validação de models, campos pendentes, geração de caso_id
- `test_processor.py`: Mock da API Claude; verifica parsing de output em 3 seções; verifica extração de campos; verifica marcadores [VERIFICAR] e ⚠️ PENDENTE
- `test_document_generator.py`: Mock de CaseOutput; verifica geração de DOCX; verifica que campos pendentes aparecem como placeholder

**Validation:**
```bash
python -m pytest tests/ -v --tb=short
```

---

### Task 9: Salvar output estruturado
**Keywords:** wire output saving, create JSON export
**Files:**
- `src/processor.py` (modify)
- `src/main.py` (modify)

**Description:**
Após processamento, salvar em `output/{caso_id}/`:
- `ficha.json` — FichaCaso serializada (Pydantic .model_dump_json())
- `panorama.md` — Seção 2 do output do Claude (texto integral)
- `output_completo.md` — Output integral do Claude (todas as 3 seções)

Adicionar método `save_output(case_output: CaseOutput, output_dir: Path)` ao processador.

**Validation:**
```bash
ls output/*/ficha.json output/*/panorama.md output/*/output_completo.md
```

---

## 7. Validation Gating

### Level 1: Syntax & Types
```bash
python -m py_compile src/main.py
python -m py_compile src/processor.py
python -m py_compile src/models.py
python -m py_compile src/document_generator.py
python -m py_compile src/prompts.py
python -m py_compile src/config.py
```
**Critério:** Zero errors em todos os módulos

### Level 2: Unit Tests
```bash
python -m pytest tests/ -v --tb=short
```
**Critério:** All tests pass

### Level 3: Integration Test (requer API key)
```bash
# Teste com briefing real de marcas
echo "Meu cliente João Silva, CPF 123.456.789-00, quer registrar a marca 'Café Premium' no INPI para classe 30 (alimentos). Ele tem CNPJ 12.345.678/0001-90 da empresa JS Alimentos LTDA. Endereço: Rua das Flores, 123, São Paulo/SP." | python -m src.main processar --stdin
```
**Critério:**
- Output gerado sem erro
- ficha.json contém matéria "Marcas"
- procuracao.docx existe e abre no Word/LibreOffice
- contrato.docx existe e abre
- panorama.md contém ao menos 1 via estratégica
- Nenhum CPF/dado inventado que não estava no briefing

### Level 4: Smoke Test Multi-Matéria
```bash
# Testar com cada fixture
for f in tests/fixtures/briefing_*.txt; do
  echo "=== Testando: $f ==="
  python -m src.main processar --arquivo "$f"
done
```
**Critério:** Todos os 3 cenários processam sem erro; matéria classificada corretamente em cada caso

---

## 8. Final Checklist

### Quality Gates
- [ ] All Level 1 validations pass (py_compile)
- [ ] All Level 2 validations pass (pytest)
- [ ] Level 3 integration test passa com API key válida
- [ ] Level 4 smoke test multi-matéria passa
- [ ] Nenhum dado inventado (CPF, nome, endereço) em outputs
- [ ] Marcadores [VERIFICAR] presentes em citações legais
- [ ] Marcadores ⚠️ PENDENTE presentes em dados faltantes
- [ ] Templates DOCX abrem corretamente em Word/LibreOffice
- [ ] .env.example documentado (sem secrets)
- [ ] output/ no .gitignore
- [ ] Nenhum console.log/print de dados sensíveis

### Patterns to Avoid
- [ ] Não inventar dados do cliente que não estão no briefing
- [ ] Não sugerir valores de honorários
- [ ] Não afirmar probabilidade de êxito com percentuais
- [ ] Não hardcodar API key (usar .env)
- [ ] Não logar conteúdo de briefings (dados sensíveis)
- [ ] Não tratar output do Claude como 100% confiável (sempre parsear defensivamente)

---

## 9. Confidence Assessment

**Score:** 7/10

**Factors:**
- [+2] Prompt já otimizado e analisado (prompt-legal-case-processor.md + analysis)
- [+1] Requisitos claros do usuário final (transcrição de áudio)
- [+1] Stack simples e bem documentada (Python + Anthropic SDK + docxtpl)
- [+1] Arquitetura MVP simples (3 etapas, sem orquestração multi-agente)
- [+1] Pydantic models para estruturar output
- [-1] Templates DOCX precisam ser criados manualmente com formatação OAB específica
- [-1] Parsing de output do Claude pode ser frágil (markdown livre, não JSON)
- [-1] Sem exemplos de output real do Claude para validar parsing
- [-1] Sem templates reais do Raphael (usando templates genéricos)

**Para aumentar confiança:**
- Obter templates reais de procuração/contrato que Raphael já usa
- Fazer 2-3 chamadas reais ao Claude com briefings de teste para calibrar parsing
- Considerar usar tool_use/structured output do Claude para garantir JSON na ficha

---

*PRP generated by dev-kit:10-generate-prp*
*IMPORTANTE: Execute em nova instância do Claude Code (use /clear antes de executar)*
