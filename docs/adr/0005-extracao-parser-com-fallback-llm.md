# ADR — Parser heurístico primeiro e modelo de linguagem como fallback

- **Estado:** Aceita (documentada retrospectivamente)
- **Data de registro:** 2026-11-27
- **Data original da decisão:** não identificada com segurança no histórico consultado
- **Base de análise:** commit `036c3481d0dba6901c92df50311ac396f4f0682a`

## Contexto

E-mails institucionais possuem alguma variação de formatação. Uma chamada de IA para todo e-mail aumentaria custo e dependência externa, mesmo em mensagens que podem ser lidas por regras determinísticas. Por outro lado, um parser puramente heurístico não cobre todos os formatos.

## Decisão

Executar primeiro o parser heurístico. Quando faltam campos obrigatórios, utilizar um modelo configurado via OpenRouter como fallback. Validar estrutura e data antes de publicar e verificar eventos ativos com título semelhante e mesma data para evitar duplicar lembretes.

## Alternativas consideradas

- **LLM em todas as mensagens:** foi evitado para reduzir chamadas externas desnecessárias.
- **Somente parser heurístico:** teria menor custo operacional, mas não cobriria mensagens com formato menos previsível.
- **Publicação sem validação:** foi rejeitada porque poderia cadastrar eventos sem título/data utilizáveis ou com data passada.

## Consequências

O caminho comum pode ser rápido e determinístico, enquanto o fallback amplia a cobertura. A integração depende de conectividade, credenciais, quota e disponibilidade do provedor. O código chama OpenRouter com o SDK `openai`; a classe interna ainda se chama `GeminiClient`. O assunto e o corpo do e-mail são enviados ao provedor quando o fallback é acionado, portanto a minimização nos logs não equivale à minimização do conteúdo transmitido.

## Evidências na implementação

`backend/app/services/extracao_email/parser.py`, `backend/app/services/extracao_email/extraction_service.py`, `backend/app/services/ia_gemini/gemini_client.py`, `backend/app/services/ia_gemini/prompt.py` e `backend/app/services/validacao/validation_service.py`.
