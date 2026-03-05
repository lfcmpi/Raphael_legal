# Projeto Raphael — Escritório Jurídico com Agentes de IA

**Data:** 04/03/2026
**Cliente:** Raphael (Advogado generalista)

---

## 1. Diagnóstico da Situação

### Quem é o Raphael
- Advogado que atuava forte em cidadania italiana (mercado pausado por mudança legislativa)
- Hoje atua como generalista, pegando casos variados (família, empresarial, marcas/patentes/franchising)
- Tem parceria com empresa de marcas, patentes e franchising que envia volume de casos
- Trabalha sozinho (advogado solo)

### O Problema Central
- **Volume vs. Valor:** Muitos casos pequenos que individualmente pagam pouco, mas tomam tempo desproporcional
- **Gargalo operacional:** Ele é o único "cérebro" — precisa analisar cada caso, redigir documentos, definir estratégia
- **IA atual é insuficiente:** Usa ChatGPT/Gemini de forma manual e conversacional, o que ainda exige muito tempo de interação
- **Custo de oportunidade:** Enquanto faz tarefas repetitivas, não consegue focar nos casos maiores e mais lucrativos

---

## 2. Se Fosse um Escritório de Advocacia: Profissionais e Competências

Para atender a demanda do Raphael com qualidade, um escritório tradicional precisaria de:

### Equipe Necessária

| Papel | Competências | O que faz no fluxo | Agente IA equivalente |
|-------|-------------|--------------------|-----------------------|
| **Advogado Sênior** (Raphael) | Estratégia jurídica, tomada de decisão, audiências, negociação | Revisão final, decisões estratégicas, assinatura, representação | Ele mesmo (humano no loop) |
| **Advogado Júnior / Estagiário** | Pesquisa jurídica, análise de legislação e jurisprudência | Pesquisar fundamentos legais, analisar viabilidade do caso | **Agente Pesquisador Jurídico** |
| **Paralegal / Assistente Jurídico** | Redação de peças, contratos, procurações | Redigir documentos padrão a partir de templates | **Agente Redator de Documentos** |
| **Secretária / Intake** | Organização, triagem, coleta de dados | Receber caso, organizar informações, classificar urgência | **Agente de Intake e Triagem** |
| **Consultor de Estratégia** | Análise de cenários, custo-benefício | Mapear opções (administrativa, extrajudicial, judicial) | **Agente Estrategista** |
| **Gestor de Prazos / Compliance** | Controle de prazos, checklist documental | Verificar se documentação está completa, alertar prazos | **Agente de Validação** |

### Custo Estimado (Escritório Tradicional)
- Advogado Júnior: R$ 3.000–5.000/mês
- Paralegal: R$ 2.500–4.000/mês
- Secretária: R$ 2.000–3.500/mês
- **Total mínimo: R$ 7.500–12.500/mês** (sem encargos)

### Custo com Agentes de IA
- Infraestrutura + APIs: **R$ 500–2.000/mês** (dependendo do volume)
- **Economia de 80–90%** no custo operacional

---

## 3. Arquitetura do Sistema de Agentes

### Fluxo do Caso Novo

```
┌─────────────────────────────────────────────────────────┐
│                    RAPHAEL (Input)                       │
│  Recebe do parceiro: dados do cliente + docs + briefing │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│              AGENTE 1 — INTAKE E TRIAGEM                 │
│                                                          │
│  • Extrai dados estruturados (nome, CPF/CNPJ, contato)  │
│  • Classifica a matéria (marcas, patentes, franchising,  │
│    consumidor, empresarial, família, etc.)               │
│  • Avalia complexidade (simples / médio / complexo)      │
│  • Identifica documentos faltantes                       │
│  • Gera ficha do caso padronizada                        │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│           AGENTE 2 — PESQUISADOR JURÍDICO                │
│                                                          │
│  • Identifica legislação aplicável                       │
│  • Busca jurisprudência relevante                        │
│  • Analisa precedentes e tendências                      │
│  • Verifica prazos prescricionais/decadenciais           │
│  • Mapeia riscos e probabilidade de êxito                │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│            AGENTE 3 — ESTRATEGISTA JURÍDICO              │
│                                                          │
│  • Monta panorama de atuação com 3 caminhos:             │
│    ┌─ Via administrativa (órgãos, INPI, Procon, etc.)   │
│    ├─ Via extrajudicial (notificação, mediação, acordo)  │
│    └─ Via judicial (ação cabível, vara, rito)            │
│  • Recomenda a melhor estratégia (custo-benefício)       │
│  • Estima honorários sugeridos                           │
│  • Estima timeline de cada via                           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│          AGENTE 4 — REDATOR DE DOCUMENTOS                │
│                                                          │
│  • Gera procuração (ad judicia / ad negotia)             │
│  • Gera contrato de honorários advocatícios              │
│  • Gera notificação extrajudicial (se aplicável)         │
│  • Gera minuta de petição inicial (se via judicial)      │
│  • Adapta templates ao caso específico                   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│            AGENTE 5 — REVISOR / VALIDADOR                │
│                                                          │
│  • Revisa consistência dos documentos                    │
│  • Verifica se dados do cliente estão corretos           │
│  • Checa se a estratégia é coerente com os fatos         │
│  • Valida formatação e padrões OAB                       │
│  • Gera checklist de pendências                          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│                 OUTPUT PARA RAPHAEL                       │
│                                                          │
│  📋 Ficha do caso (dados estruturados)                   │
│  📊 Panorama estratégico (3 vias com prós/contras)       │
│  📄 Procuração pronta para assinar                       │
│  📄 Contrato de honorários pronto                        │
│  📄 Notificação extrajudicial (se aplicável)             │
│  📄 Minuta de petição (se via judicial)                  │
│  ✅ Checklist de pendências e próximos passos            │
│  ⏱️ Timeline estimada                                    │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Áreas de Atuação a Cobrir (por prioridade)

### Prioridade 1 — Parceria Marcas/Patentes/Franchising
1. **Registro de marca** — pedido no INPI, acompanhamento, oposição
2. **Contratos de franquia** — COF, pré-contrato, contrato de franquia
3. **Contratos de licenciamento** — uso de marca, patente, know-how
4. **Disputas de marca** — oposição, nulidade, contrafação
5. **Registro de patente** — análise de patenteabilidade, redação, acompanhamento

### Prioridade 2 — Casos Gerais (Generalista)
6. **Direito do consumidor** — reclamações, ações de dano, CDC
7. **Direito empresarial** — contratos, abertura/alteração de sociedade
8. **Direito de família** — divórcio, pensão, guarda
9. **Direito civil** — cobranças, responsabilidade civil, contratos

### Prioridade 3 — Especialidade Anterior
10. **Cidadania italiana** — acompanhamento do julgamento constitucional, retomada se lei mudar

---

## 5. Entregáveis do Projeto (Fases)

### Fase 1 — MVP (2-4 semanas)
- [ ] Agente de Intake: recebe texto/briefing e gera ficha estruturada do caso
- [ ] Agente Redator: gera procuração e contrato de honorários a partir da ficha
- [ ] Templates base: procuração ad judicia, procuração ad negotia, contrato de honorários
- [ ] Interface simples: Raphael envia caso por WhatsApp/formulário, recebe documentos

### Fase 2 — Inteligência Estratégica (4-6 semanas)
- [ ] Agente Pesquisador: pesquisa legislação e jurisprudência aplicável
- [ ] Agente Estrategista: gera panorama com 3 vias de atuação
- [ ] Base de conhecimento jurídico por área (marcas, consumidor, empresarial, etc.)
- [ ] Templates adicionais: notificação extrajudicial, minutas por área

### Fase 3 — Automação Completa (6-8 semanas)
- [ ] Agente Revisor: validação cruzada de documentos
- [ ] Pipeline completo: caso entra → documentos saem sem intervenção
- [ ] Dashboard para Raphael acompanhar casos em andamento
- [ ] Integração com calendário para prazos

### Fase 4 — Escala (futuro)
- [ ] Múltiplos parceiros enviando casos
- [ ] Métricas de performance (casos/mês, tempo médio, receita)
- [ ] Aprendizado contínuo: agentes melhoram com feedback do Raphael

---

## 6. Stack Tecnológica Sugerida

| Componente | Tecnologia | Justificativa |
|-----------|-----------|---------------|
| Orquestração de agentes | Claude Agent SDK / CrewAI | Multi-agentes conversando entre si |
| LLM principal | Claude (Anthropic) | Melhor para textos longos e jurídicos em PT-BR |
| Geração de documentos | Python + docxtpl / WeasyPrint | Gerar DOCX e PDF formatados |
| Interface de entrada | WhatsApp API ou Formulário Web | Canal que Raphael já usa |
| Armazenamento | PostgreSQL + S3 | Dados dos casos e documentos |
| Deploy | VPS ou Cloud Functions | Rodar agentes em background |

---

## 7. Riscos e Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| IA gerar informação jurídica incorreta | Alto | Raphael sempre revisa antes de usar (humano no loop) |
| Templates desatualizados (mudança de lei) | Médio | Base de templates versionada e revisada periodicamente |
| Dados sensíveis de clientes | Alto | Criptografia, sem armazenamento desnecessário, LGPD |
| Dependência de API externa | Médio | Fallback entre provedores (Claude / GPT) |
| Cliente espera que IA substitua advogado | Baixo | Posicionar como ferramenta de produtividade, não substituição |

---

## 8. Modelo de Precificação para Raphael

### Opção A — Projeto Fixo + Manutenção
- Desenvolvimento do MVP: R$ X
- Fases adicionais: R$ Y por fase
- Manutenção mensal: R$ Z (suporte + atualizações + APIs)

### Opção B — Assinatura Mensal
- Plano mensal que inclui desenvolvimento progressivo + uso das APIs
- Escala com o volume de casos

### Opção C — Revenue Share
- Custo reduzido de desenvolvimento
- % sobre o ganho de produtividade (casos adicionais que ele consegue pegar)

---

## Próximos Passos

1. **Validar este planejamento com Raphael** — confirmar prioridades e expectativas
2. **Coletar templates reais** — pedir modelos de procuração, contrato e documentos que ele já usa
3. **Mapear o fluxo atual dele** — como ele recebe os casos hoje do parceiro (WhatsApp? Email? Formulário?)
4. **Definir escopo do MVP** — o que gera mais valor com menos esforço
5. **Estimar custos e timeline** — baseado no escopo definido
