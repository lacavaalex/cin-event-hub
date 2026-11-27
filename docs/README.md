# Documentação

Índice da documentação do CIn Event Hub. Para uma visão geral do sistema (arquitetura, banco de dados e como executar), comece pelo [README do projeto](../README.md).

## Organização

```text
docs/
├── architecture/
│   ├── overview.md          visão de arquitetura
│   ├── data-model.md        modelo de dados vigente
│   ├── diagrams/            diagramas C4, UML e de processo
│   └── database/            modelagem do banco e registros da migração para PostgreSQL
├── adr/                     registros de decisão arquitetural
├── operations/              desenvolvimento local e prontidão para produção
├── testing/                 estratégia de testes
├── workflow/                contribuição e fluxo Git
├── requirements/
│   └── backlog/             backlog de requisitos (versões 1 a 4)
├── planning/
│   └── sprint-burndowns/    gráficos de burndown das sprints
├── design/                  padronização de design e identidade visual
├── reports/
│   ├── deliveries/          relatórios das entregas da disciplina
│   ├── individual/          relatórios individuais de contribuição
│   ├── technical/           notas técnicas de decisões de implementação
│   └── testing/             roteiro, registros e relatórios de execução de testes
├── presentations/
│   ├── slides/              slides das entregas
│   └── final-pitch/         apresentação final e material de apoio
├── guides/                  guias de execução e contribuição
└── references/              material de referência da disciplina
```

> **Fonte da verdade:** para a estrutura do banco prevalece [`database/001_schema.sql`](../database/001_schema.sql); para o comportamento, o código. Diagramas, entregas e documentos antigos registram o momento em que foram produzidos.

## Referência técnica

| Documento | Conteúdo |
|---|---|
| [`architecture/overview.md`](architecture/overview.md) | Arquitetura geral, monólito modular, três camadas, componentes e fluxo de extração |
| [`architecture/data-model.md`](architecture/data-model.md) | Tabelas, colunas, relacionamentos e restrições atuais |
| [`adr/`](adr/README.md) | Nove decisões de arquitetura, com alternativas e consequências |
| [`operations/local-development.md`](operations/local-development.md) | PostgreSQL, variáveis de ambiente, execução e testes locais |
| [`operations/production-readiness.md`](operations/production-readiness.md) | Riscos e verificações pendentes antes de uma implantação pública |
| [`testing/strategy.md`](testing/strategy.md) | Suítes, comandos, pré-requisitos e limites dos testes |
| [`workflow/contributing.md`](workflow/contributing.md) | Branches, pull requests, documentação e ADRs |

## Requisitos

| Documento | Conteúdo |
|---|---|
| [`Backlog_v4.pdf`](requirements/backlog/Backlog_v4.pdf) | Backlog de requisitos vigente: épicos, histórias de usuário, critérios de aceite e priorização MoSCoW |
| [`Backlog_v1.pdf`](requirements/backlog/Backlog_v1.pdf), [`v2`](requirements/backlog/Backlog_v2.pdf), [`v3`](requirements/backlog/Backlog_v3.pdf) | Versões anteriores, mantidas como histórico de evolução do escopo |

## Arquitetura

| Documento | Conteúdo |
|---|---|
| [`diagrams/IESI_C4_n1_Entrega_3.drawio`](architecture/diagrams/IESI_C4_n1_Entrega_3.drawio) | C4 nível 1 (contexto) |
| [`diagrams/IESI_C4_n2_Entrega_3.drawio`](architecture/diagrams/IESI_C4_n2_Entrega_3.drawio) | C4 nível 2 (contêineres) |
| [`diagrams/IESI_UML_Entrega_3.drawio`](architecture/diagrams/IESI_UML_Entrega_3.drawio) ([`.png`](architecture/diagrams/IESI_UML_Entrega_3.drawio.png)) | Diagrama de implantação |
| [`diagrams/IESI_Fluxo.drawio.png`](architecture/diagrams/IESI_Fluxo.drawio.png) | Processo de divulgação de eventos: cenário atual e cenário proposto |
| [`database/modelo-eer.drawio`](architecture/database/modelo-eer.drawio) | Modelo EER do banco |
| [`database/modelo-relacional.drawio`](architecture/database/modelo-relacional.drawio) | Modelo relacional |
| [`database/migracao-postgresql.md`](architecture/database/migracao-postgresql.md) | Migração do backend de SQLite para PostgreSQL: decisões e trade-offs |
| [`database/refatoracao-banco.md`](architecture/database/refatoracao-banco.md) | Refatoração do banco de dados e dos testes |

Os diagramas das entregas e os modelos do banco retratam o projeto na época em que foram produzidos. O modelo vigente está em [`data-model.md`](architecture/data-model.md) e no [README do projeto](../README.md); a documentação antiga do banco cita tabelas que não existem mais (`email_associado`, `admins`).

## Design

| Documento | Conteúdo |
|---|---|
| [`template-padronizacao-visual-us-7-1.md`](design/template-padronizacao-visual-us-7-1.md) | Template de padronização de design e identidade visual (US 7.1): tokens, tipografia, componentes, temas claro e escuro, acessibilidade e modelo de auditoria por tela |

## Planejamento

| Documento | Conteúdo |
|---|---|
| [`sprint-burndowns/`](planning/sprint-burndowns/) | Burndown das Sprints 0, 1, 2A, 2B, 3 e 4, exportados do Jira |

## Relatórios

| Documento | Conteúdo |
|---|---|
| [`deliveries/IESI_Entrega_1.pdf`](reports/deliveries/IESI_Entrega_1.pdf) a [`IESI_Entrega_4.pdf`](reports/deliveries/IESI_Entrega_4.pdf) | Problema e diagnóstico, modelagem de processos, proposta de arquitetura, implementação inicial e gerenciamento do projeto |
| [`technical/lgpd-minimizacao-dados.md`](reports/technical/lgpd-minimizacao-dados.md) | Minimização de dados pessoais na extração de e-mails |
| [`technical/paginacao-eventos.md`](reports/technical/paginacao-eventos.md) | Contrato e implementação da paginação de `GET /events` |
| [`individual/relatorio-individual_erlon-matheus_frontend.pdf`](reports/individual/relatorio-individual_erlon-matheus_frontend.pdf) | Relatório individual de contribuições (front-end), Sprints 1 a 3 |
| [`testing/`](reports/testing/README.md) | Roteiro de testes, registro de execução, relatório de jornadas e auditoria E2E, em ordem cronológica (a estratégia de testes está em [`testing/strategy.md`](testing/strategy.md)) |

## Apresentações

| Documento | Conteúdo |
|---|---|
| [`slides/Entrega_2_Slide.pdf`](presentations/slides/Entrega_2_Slide.pdf), [`3`](presentations/slides/Entrega_3_Slide.pdf), [`4`](presentations/slides/Entrega_4_Slide.pdf) | Slides das Entregas 2, 3 e 4 |
| [`final-pitch/Hub_de_Eventos_Pitch_IESI.pptx`](presentations/final-pitch/Hub_de_Eventos_Pitch_IESI.pptx) | Apresentação final (8 slides, com notas do apresentador) |
| [`final-pitch/roteiro-apresentacao.md`](presentations/final-pitch/roteiro-apresentacao.md) | Roteiro de fala |
| [`final-pitch/guia-qa.md`](presentations/final-pitch/guia-qa.md) | Perguntas prováveis e respostas |
| [`final-pitch/mapa-fundamentacao.md`](presentations/final-pitch/mapa-fundamentacao.md) | Fundamentação de cada afirmação dos slides |

## Guias

| Documento | Conteúdo |
|---|---|
| [`contribuidores-docker.pdf`](guides/contribuidores-docker.pdf) | Ambiente com Docker Compose e comandos essenciais |
| [`integracao-openrouter-execucao-local.pdf`](guides/integracao-openrouter-execucao-local.pdf) | Integração com o provedor de IA e execução local |

## Referências

| Documento | Conteúdo |
|---|---|
| [`Integracao_de_Dados_template-apresentacao.pdf`](references/Integracao_de_Dados_template-apresentacao.pdf) | Apresentação-modelo da disciplina |

## Convenções

- Notas técnicas em Markdown, com nome em minúsculas e hifens.
- Documentos de entrega mantêm o nome original (`IESI_Entrega_N`, `Backlog_vN`), pois são citados nos próprios relatórios.
- O formato original é preservado: diagramas em `.drawio` (com o `.png` exportado, quando existe), apresentações e relatórios em `.pdf`.
- Decisões de arquitetura novas viram um ADR com o próximo número (modelo em [`adr/README.md`](adr/README.md)).
- Todo documento novo entra na tabela da sua seção neste índice.
