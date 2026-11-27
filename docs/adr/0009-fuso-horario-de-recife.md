# ADR — Usar America/Recife como referência temporal do domínio

- **Estado:** Aceita (documentada retrospectivamente)
- **Data de registro:** 2026-11-27
- **Data original da decisão:** não identificada com segurança no histórico consultado
- **Base de análise:** commit `036c3481d0dba6901c92df50311ac396f4f0682a`

## Contexto

O projeto é destinado à comunidade do CIn/UFPE. Datas de eventos e rotinas administrativas precisam ter comportamento previsível mesmo quando o servidor ou o CI executa em UTC.

## Decisão

Usar `America/Recife` para obter a data de referência das regras de negócio e configurar os schedulers. Persistir datas e horas de início/fim de evento como `DATE` e `TIME`, pois representam o horário local informado para o evento; persistir timestamps técnicos como `TIMESTAMPTZ`. A data de cadastro do usuário usa explicitamente o deslocamento UTC-3 no default SQL.

## Alternativas consideradas

- **Usar o fuso local do servidor:** foi evitado porque depende do ambiente de execução e pode divergir entre desenvolvimento, CI e produção.
- **Tratar todas as datas de evento como UTC:** não representa diretamente o horário local divulgado ao público.

## Consequências

Regras de passado/expiração e agendamentos usam um referencial local consistente. Como o início/fim do evento são `DATE` e `TIME`, não carregam fuso individual; qualquer integração que passe a aceitar eventos em múltiplos fusos exigirá uma decisão de modelagem adicional.

## Evidências na implementação

`backend/app/services/extracao_email/parser.py`, `backend/app/services/validacao/validation_service.py`, `backend/app/services/events/cleanup_service.py`, `backend/app/services/events/cleanup_scheduler.py` e `database/001_schema.sql`.
