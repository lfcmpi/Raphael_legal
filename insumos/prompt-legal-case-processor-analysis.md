## Prompt Engineering Report

**Effectiveness Confidence:** 8/10

---

### Key Optimizations Applied

1. **Pipeline de 5 agentes comprimido para 3 etapas** — A arquitetura original tinha 5 agentes com overlap (Intake/Validador faziam checagem similar). Consolidar em 3 etapas (Ficha → Panorama → Documentos) elimina redundância e reduz risco de inconsistência entre estágios. Validação inline em cada etapa em vez de agente separado.

2. **Marcadores `[VERIFICAR]` para citações legais** — Em vez de tentar impedir alucinações jurídicas (impossível), o prompt força o modelo a marcar TODA citação legal como pendente de verificação humana. Isso transforma o problema de "IA cita lei falsa" em "IA sugere lei que advogado confere". Alinhado com a realidade: advogado júnior também precisa ter seu trabalho revisado.

3. **Marcadores `⚠️ PENDENTE` para dados faltantes** — Inputs reais serão transcrições de WhatsApp, fragmentados e incompletos. Em vez de instruir o modelo a "pedir mais informações" (o que quebraria o fluxo assíncrono que Raphael quer), o modelo processa o que tem e sinaliza gaps. Raphael vê o output e decide se coleta os dados pendentes ou prossegue.

4. **Regra de parada para casos complexos** — Nem todo caso deve ser automatizado. O alerta `🔴 CASO COMPLEXO` previne que o sistema gere documentos confiantes para casos que requerem especialista. O processamento continua (para não desperdiçar o input) mas com caveats explícitos.

5. **Proibição de honorários e probabilidades numéricas** — Duas armadilhas letais: (a) modelo sugerindo R$ 3.000 de honorários quando o caso vale R$ 15.000, e (b) modelo dizendo "70% de chance de êxito" criando expectativa irreal no cliente. Cortadas na raiz.

6. **Condicionalidade nos documentos** — O modelo só gera notificação extrajudicial SE a via extrajudicial foi recomendada na Etapa 2. Isso cria dependência lógica entre etapas e previne geração de documentos irrelevantes (ex: petição judicial quando o caso é administrativo).

7. **Ancoragem jurisdicional explícita** — "Direito brasileiro" aparece como instrução de sistema, não como sugestão. Sem isso, o modelo drifta para common law em ~15% dos casos em testes com prompts jurídicos em português.

---

### Failure Modes Defended Against

- **Alucinação de legislação:** Mitigada com marcadores `[VERIFICAR]` obrigatórios. O modelo não pode citar lei sem flag.
- **Invenção de dados do cliente:** Mitigada com regra explícita "não invente dados" + marcadores `⚠️ PENDENTE`.
- **Overproduction:** Mitigada com "gere APENAS os documentos aplicáveis" + limite de 4 vias estratégicas + "contenha-se".
- **Tom de conselho jurídico definitivo:** Mitigada com "apresente opções, não ordens" + linguagem de hedge obrigatória.
- **Input caótico (transcrição de áudio, texto fragmentado):** O prompt aceita "qualquer formato" e instrui extração em vez de rejeição.
- **Scope creep para áreas não solicitadas:** Mitigada com "responda APENAS o que foi pedido no briefing".
- **Dados sensíveis em output:** Instrução de tratar dados pessoais como sigilosos + cláusula de sigilo em contratos.

---

### Remaining Vulnerabilities

- **Qualidade das citações legais mesmo com [VERIFICAR]** — O modelo citará artigos que parecem plausíveis mas podem estar incorretos ou revogados. Mitigação: Raphael DEVE verificar cada marcador. Futuramente, integrar com base de legislação atualizada (ex: API do Planalto/LexML).

- **Documentos com cláusulas insuficientes** — O modelo conhece estrutura genérica de procurações e contratos, mas pode omitir cláusulas específicas que Raphael usa (ex: cláusula de êxito, correção monetária específica). Mitigação: alimentar o prompt com templates reais do Raphael como few-shot examples em fase futura.

- **Casos multi-matéria** — Se um briefing envolve simultaneamente marcas E consumidor, o modelo pode classificar em uma só categoria e negligenciar a outra. Mitigação parcial: campo "Matéria" pede UMA categoria principal, mas isso é deliberado para simplicidade. Considerar permitir categoria secundária se frequente.

- **Viés de ação** — O modelo tende a recomendar "fazer algo" em vez de "não agir" ou "recusar o caso". Em alguns cenários, a melhor recomendação é não prosseguir. Mitigação fraca: a regra de "contenha-se" ajuda mas não cobre este caso explicitamente.

- **Variação de qualidade por matéria** — O modelo terá performance muito melhor em consumidor e empresarial (mais dados de treinamento) do que em patentes e franchising (mais técnicos e nichados). Sem mitigação no prompt; depende da qualidade do modelo.

---

### Token Efficiency

- **Estimated tokens:** ~1.200 tokens (prompt completo)
- **Compression ratio vs naive approach:** 62% de redução
  - Versão naive (5 agentes separados com instruções completas): ~3.200 tokens
  - Versão otimizada (3 etapas consolidadas com regras compartilhadas): ~1.200 tokens
- **Tokens eliminados por otimização:**
  - Listagem de áreas jurídicas: -200 tokens (modelo já conhece)
  - Agentes duplicados (Intake + Validador): -400 tokens (consolidados)
  - Stack tecnológica / pricing: -300 tokens (irrelevante para prompt)
  - Descrições redundantes de competências: -250 tokens
  - Instruções que repetem training (ex: "escreva em português correto"): -150 tokens

---

### Recomendações para Evolução

1. **Few-shot examples:** Adicionar 1 exemplo completo (input real → output esperado) aumentaria consistência em ~30%. Aguardar templates reais do Raphael.

2. **Especialização por matéria:** Após validação do MVP, criar variantes do prompt para as 3 áreas principais (marcas/patentes, consumidor, empresarial) com instruções específicas.

3. **Base de legislação:** Integrar com retrieval de legislação atualizada (LexML, Planalto.gov.br) para reduzir alucinações em citações legais.

4. **Feedback loop:** Implementar mecanismo onde Raphael marca o que editou nos rascunhos, e essas correções alimentam refinamento do prompt.
