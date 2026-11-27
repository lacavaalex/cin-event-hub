# Registros de Decisão Arquitetural (ADRs)

Os ADRs registram decisões estruturais do CIn Event Hub, as alternativas consideradas e as consequências para manutenção e evolução do sistema.

## Critério de leitura

Os registros abaixo foram elaborados retrospectivamente em **27/11/2026**, com base no código no commit `036c3481d0dba6901c92df50311ac396f4f0682a`. A data original de cada decisão não foi recuperada com segurança no histórico consultado. Portanto, `Aceita (documentada retrospectivamente)` significa que a decisão corresponde à implementação analisada; não significa que exista uma ata formal da data em que a equipe originalmente a tomou.

## Índice

| ADR | Decisão | Estado |
|---|---|---|
| [0001](0001-monolito-modular-e-camadas.md) | Backend como monólito modular organizado em camadas | Aceita (documentada retrospectivamente) |
| [0002](0002-frontend-spa-e-api-rest.md) | Frontend SPA separado da API REST | Aceita (documentada retrospectivamente) |
| [0003](0003-postgresql-e-schema-sql-como-referencia.md) | PostgreSQL e schema SQL versionado como referência física | Aceita (documentada retrospectivamente) |
| [0004](0004-usuario-unico-e-perfil-administrador.md) | Uma entidade `usuario`; administração por `is_admin` | Aceita (documentada retrospectivamente) |
| [0005](0005-extracao-parser-com-fallback-llm.md) | Parser heurístico primeiro e LLM como fallback via OpenRouter | Aceita (documentada retrospectivamente) |
| [0006](0006-log-de-extracao-e-minimizacao.md) | Log idempotente e minimização de dados persistidos | Aceita (documentada retrospectivamente) |
| [0007](0007-agendamento-com-apscheduler.md) | Rotinas agendadas com APScheduler no processo da API | Aceita (documentada retrospectivamente) |
| [0008](0008-autenticacao-administrativa-jwt.md) | Autenticação administrativa com bcrypt e JWT | Aceita (documentada retrospectivamente) |
| [0009](0009-fuso-horario-de-recife.md) | `America/Recife` como referência de data e agendamento | Aceita (documentada retrospectivamente) |

## Quando criar um novo ADR

Crie um ADR quando a equipe precisar decidir algo que afete arquitetura, persistência, segurança, integração externa, infraestrutura ou operação e que seja útil conhecer no futuro. Correções locais, mudanças de texto e refatorações sem alteração de comportamento não exigem ADR.

Use o próximo número sequencial. Não apague um ADR aceito: marque-o como `Substituído` e indique o ADR que o substitui. Registre decisões ainda não tomadas como propostas fora da sequência de ADRs aceitos.

## Modelo

```markdown
# ADR-NNNN — Título curto

- **Estado:** Proposto | Aceito | Rejeitado | Substituído
- **Data de registro:** AAAA-MM-DD
- **Data original da decisão:** se conhecida; caso contrário, “não identificada”

## Contexto
Qual problema ou necessidade motivou a decisão?

## Decisão
O que foi escolhido?

## Alternativas consideradas
Quais opções foram avaliadas e por que não foram adotadas?

## Consequências
Benefícios, custos, riscos e limitações.

## Evidências na implementação
Arquivos, configurações, testes ou PRs que materializam a decisão.
```
