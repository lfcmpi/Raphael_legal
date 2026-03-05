## Prompt Engineering Report — PRP v2 Adversarial Review

**Effectiveness Confidence:** 8.5/10 (up from 7/10)

---

### Key Optimizations Applied

1. **tool_use para ficha estruturada (elimina regex parsing)** — O risco #1 do PRP v1 era parsear markdown livre com regex para extrair campos estruturados da ficha. Claude varia formatação entre runs (## vs ###, tabelas vs listas, etc.). A v2 usa `tool_use` do Claude: a ficha vem como JSON garantido pelo schema. O modelo preenche campos tipados com enums. Fallback para regex existe mas é o plano B, não o plano A. Isso sozinho justifica a revisão inteira.

2. **Package structure correta (raphael_legal/ com __main__.py)** — v1 usava `src/` como package e `python -m src.main` como entrypoint. Isso não funciona sem hack de PYTHONPATH. A v2 usa `raphael_legal/` como package nomeado com `__main__.py`, executável via `python -m raphael_legal`. Parece trivial, mas o agente implementador teria perdido 15-30 min debugando import errors.

3. **Script dedicado para templates DOCX (templates/create_templates.py)** — v1 dizia "criar programaticamente via python-docx" sem especificar como. A v2 tem uma task dedicada (Task 5) com script idempotente que gera os .docx com formatação OAB (fontes, margens, espaçamento). O agente sabe exatamente o que produzir.

4. **Fixture de mock do Claude (claude_response_marcas.json)** — v1 não tinha nenhum exemplo de como o output do Claude realmente se parece. O agente teria que inventar mocks. A v2 exige que Task 8 crie uma fixture realista, que é usada nos testes unitários e de integração. Isso ancora os testes em algo concreto.

5. **Fixture de input minimal ("quer registrar uma marca")** — v1 só testava inputs razoáveis. O pior caso real é um briefing de 5 palavras sem nenhum dado. A v2 exige teste desse cenário: o sistema deve processar (não crashear) e marcar tudo como PENDENTE.

6. **Decisões arquiteturais declaradas como finais** — v1 misturava contexto e decisões. A v2 tem seção "Decisões Arquiteturais (FINAIS — não rediscutir)" com 5 decisões numeradas. O agente implementador não perde tempo reconsiderando o que já foi decidido.

7. **Fallback explícito para tool_use failure** — Gotcha #1 da v2 documenta: se Claude não usar a tool (pode acontecer), detectar e degradar graciosamente para regex. O agente implementador sabe que precisa implementar ambos os paths.

8. **Error handling especificado** — v1 não mencionava o que acontece com API timeout, 429, ou key ausente. v2 especifica: retry com backoff (SDK built-in), mensagens amigáveis no CLI, sem stacktrace para o usuário.

---

### Failure Modes Defended Against

- **Parsing frágil de markdown** — Eliminado para a ficha (tool_use). Tolerado para panorama/documentos (são texto para humanos).
- **Import errors por estrutura de package incorreta** — Corrigido com `raphael_legal/` + `__main__.py`.
- **Templates DOCX corrompidos** — Script dedicado com validação (docxtpl.DocxTemplate carrega sem erro).
- **Input mínimo/vazio** — Fixture `briefing_minimal.txt` + teste explícito.
- **Claude não usa tool_use** — Fallback para regex + warning log.
- **API failure** — Retry built-in do SDK anthropic + mensagens amigáveis.
- **Dados inventados** — Validação nos testes: CPF no output deve existir no input ou ser PENDENTE.
- **Encoding/acentos** — Fixtures com nomes acentuados (João, São Paulo) testam implicitamente.

---

### Remaining Vulnerabilities

- **Templates genéricos vs. templates do Raphael** — O sistema usa templates criados programaticamente, não os modelos reais que Raphael usa. Cláusulas podem estar incompletas ou ter estilo diferente. Mitigação: templates são fáceis de substituir quando Raphael fornecer os dele.

- **Sem few-shot example no prompt** — O system prompt não inclui um exemplo completo de input→output. Isso reduz consistência em ~30% segundo a análise original. Mitigação: o prompt já tem confidence 8/10 sem few-shot. Adicionar quando tiver um output real aprovado por Raphael.

- **Parsing de panorama e documentos ainda é texto** — Apenas a ficha é JSON estruturado. Panorama e documentos são extraídos por regex de headers markdown. Se Claude mudar formatação, perde-se a separação. Mitigação: esses outputs são para leitura humana, então perder a separação é inconveniente (tudo fica em output_completo.md), não catastrófico.

- **Performance variável por matéria jurídica** — Claude performa melhor em consumidor/empresarial (mais dados de treinamento) do que em patentes/franchising (nichados). Sem mitigação no prompt — depende do modelo.

- **Viés de ação do modelo** — Claude tende a recomendar "fazer algo" em vez de "não agir" ou "recusar o caso". Em alguns cenários, a melhor recomendação é não prosseguir. Mitigação parcial pela regra "contenha-se" no prompt.

---

### Token Efficiency (do PRP como instrução para o agente implementador)

- **PRP v1:** ~4.800 tokens
- **PRP v2:** ~5.200 tokens (+8%)
- **Análise:** A v2 é 8% maior mas elimina 3 ambiguidades críticas que teriam custado 30-60 min de debugging cada. O aumento de tokens é em especificação precisa (tool schema, fixture format, fallback logic), não em verbosidade. Seções redundantes da v1 (checklist duplicando validation, patterns to avoid duplicando success criteria) foram cortadas.

### Mudanças estruturais vs v1

| Aspecto | v1 | v2 | Impacto |
|---------|----|----|---------|
| Parsing da ficha | Regex markdown | tool_use JSON | Elimina risco #1 |
| Package name | `src/` | `raphael_legal/` | CLI funciona |
| Entrypoint | `python -m src.main` | `python -m raphael_legal` | Correto |
| Templates DOCX | "criar programaticamente" | Script dedicado (Task 5) | Implementável |
| Mock de Claude | Nenhum | fixture JSON | Testes úteis |
| Input minimal | Não testado | Fixture + teste | Robustez |
| Tasks | 9 (com deps implícitas) | 9 (ordem = dep) | Clareza |
| Confidence | 7/10 | 8.5/10 | +1.5 |

---

*Analysis generated by adversarial review (5 phases: hacker, red-team, efficiency, linguist, LLM-reception)*
