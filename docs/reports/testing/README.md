# Testes

Documentos de planejamento e de resultado de testes do CIn Event Hub, em ordem cronológica. Os relatórios de resultado são fotografias de um commit da `develop`; o código mudou depois de cada um.

| Documento | Data | Conteúdo | Base |
|---|---|---|---|
| [`roteiro-de-testes.md`](roteiro-de-testes.md) | 15/11/2026 | Plano de testes do MVP 1.0: banco, back-end e front-end revisados em dupla, depois integração ponta a ponta, rastreados ao backlog e à Definição de Pronto | Schema e código da época |
| [`registro-de-testes.md`](registro-de-testes.md) | 22/11/2026 | Registro da execução dos testes de banco, back-end e front-end e do ambiente necessário para rodá-los | `develop` @ `c131e9d` |
| [`relatorio-e2e-jornada-2026-11-22.md`](relatorio-e2e-jornada-2026-11-22.md) | 22/11/2026 | Execução das jornadas de usuário (casos INT e NF do roteiro), com resultado por caso e defeitos encontrados | `develop` @ `c131e9d` |
| [`auditoria-e2e-2026-11-26.md`](auditoria-e2e-2026-11-26.md) | 26/11/2026 | Auditoria em sete camadas (banco, back-end, E2E local, produção no Render, front-end local, Docker e front-end na Vercel), com catálogo de defeitos e plano de ação | `develop` @ `9668957` |

O resultado mais recente é o da auditoria de 26/11. O roteiro continua sendo a referência dos casos de teste, mas descreve o schema da época em que foi escrito: o schema vigente é o `database/001_schema.sql`.
