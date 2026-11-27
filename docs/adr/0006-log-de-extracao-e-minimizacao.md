# ADR — Log de extração idempotente e minimização de dados persistidos

- **Estado:** Aceita (documentada retrospectivamente)
- **Data de registro:** 2026-11-27
- **Data original da decisão:** não identificada com segurança no histórico consultado
- **Base de análise:** commit `036c3481d0dba6901c92df50311ac396f4f0682a`

## Contexto

A varredura periódica pode encontrar a mesma mensagem mais de uma vez. É necessário evitar reprocessamento e manter um histórico operacional de mensagens aceitas, ignoradas, descartadas ou com falha. Ao mesmo tempo, o corpo integral dos e-mails pode conter dados pessoais que não são necessários para auditoria da extração.

## Decisão

Persistir um registro por `gmail_message_id` em `extracao`, com restrição UNIQUE. Não persistir o corpo integral do e-mail. Armazenar apenas o domínio do remetente em `source_email` e mascarar e-mails, CPFs e telefones nos campos livres do log (`extracted_data` e `error_message`). Preservar o log quando o evento associado for removido, definindo `event_id` como nulo.

## Alternativas consideradas

- **Persistir o e-mail completo:** facilitaria depuração, mas aumentaria a retenção de dados pessoais sem necessidade funcional.
- **Não manter logs:** reduziria dados persistidos, mas eliminaria a rastreabilidade de falhas e resultados.
- **Apagar logs junto com eventos:** destruiria o histórico operacional; foi adotado `ON DELETE SET NULL`.

## Consequências

A aplicação consegue detectar mensagens repetidas e manter o histórico de processamento. A minimização documentada se aplica aos dados persistidos nos logs. O fallback de IA ainda recebe o assunto e o corpo originais; antes de usar dados institucionais reais, a equipe deve avaliar a base legal, os termos de tratamento, a retenção e a configuração de privacidade do provedor externo.

## Evidências na implementação

`database/001_schema.sql`, `backend/app/models/extraction_log.py`, `backend/app/repositories/extraction_log_repository.py`, `backend/app/services/extracao_email/minimizacao.py` e `backend/app/services/extracao_email/extraction_service.py`. Complemento histórico: `docs/reports/technical/lgpd-minimizacao-dados.md`.
