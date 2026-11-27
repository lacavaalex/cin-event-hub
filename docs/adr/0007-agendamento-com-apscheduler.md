# ADR — Executar rotinas recorrentes com APScheduler no processo FastAPI

- **Estado:** Aceita (documentada retrospectivamente)
- **Data de registro:** 2026-11-27
- **Data original da decisão:** não identificada com segurança no histórico consultado
- **Base de análise:** commit `036c3481d0dba6901c92df50311ac396f4f0682a`

## Contexto

O sistema precisa buscar mensagens novas periodicamente e remover eventos cuja data limite já passou, sem depender de acionamento manual constante. Para o escopo atual, não existe um serviço de mensageria ou worker distribuído separado.

## Decisão

Utilizar APScheduler em background no mesmo processo da API. O job de extração usa intervalo configurável (`EXTRACTION_INTERVAL_MINUTES`, padrão 720 minutos). A limpeza usa CRON diário às 03:00 em `America/Recife`, salvo quando `CLEANUP_INTERVAL_MINUTES` define intervalo alternativo. Os schedulers são iniciados e encerrados pelo `lifespan` do FastAPI.

## Alternativas consideradas

- **Worker ou serviço de scheduler separado:** ofereceria isolamento e controle de escala, mas exigiria infraestrutura adicional.
- **Execução apenas manual:** não atenderia à atualização periódica dos eventos e à limpeza automática.

## Consequências

A configuração é simples e adequada a uma instância única. Como os jobs vivem dentro do processo web, múltiplas réplicas/workers podem agendar a mesma rotina mais de uma vez. Uma implantação escalada deve mover o scheduler para um único worker ou serviço dedicado e implementar coordenação distribuída.

## Evidências na implementação

`backend/app/main.py`, `backend/app/services/extracao_email/scheduler.py`, `backend/app/services/events/cleanup_scheduler.py` e `backend/app/services/events/cleanup_service.py`.
