# Prontidão para produção

Este documento não certifica o sistema como pronto para produção. Ele registra verificações derivadas do código em 27/11/2026 e separa o que já existe do que ainda precisa ser validado.

## 1. Resumo executivo

O projeto já possui separação frontend/API, autenticação administrativa JWT, persistência PostgreSQL, integração OAuth de leitura do Gmail, log de extração e testes automatizados. Entretanto, há pontos que precisam ser tratados antes de expor a aplicação publicamente, principalmente CORS, identidade dos usuários de favoritos, conteúdo enviado ao provedor de IA, configuração de containers e execução duplicada de schedulers.

## 2. Itens prioritários

| Prioridade | Item | Estado observado | Ação necessária |
|---|---|---|---|
| Crítica | CORS | `main.py` usa `allow_origins=["*"]` e permite credenciais. | Ler uma lista de origens permitidas da configuração e restringi-la aos domínios reais do frontend. |
| Crítica | Identidade de alunos/favoritos | Rotas de favoritos recebem `X-User-Id`; o frontend atual envia um identificador estático no cliente HTTP. | Implementar autenticação/identidade de aluno no servidor e derivar o ID do token/sessão, nunca de um cabeçalho arbitrário do cliente. |
| Crítica | Envio de conteúdo ao LLM | O fallback constrói o prompt com assunto e corpo do e-mail integral. A minimização atual ocorre ao persistir logs. | Avaliar base legal, autorização institucional, termos de tratamento e retenção do provedor; considerar sanitização/minimização antes do envio. |
| Alta | Healthcheck do backend | O Dockerfile consulta `/health`, mas `main.py` expõe `GET /` como health check. | Alinhar o healthcheck com uma rota real ou criar a rota `/health`; validar o estado do container. |
| Alta | Variáveis do Docker Compose | O Compose injeta variáveis de Gmail e CORS diferentes das que o código atual lê. | Alinhar Compose, `.env.example`, `config.py` e GmailClient; testar build e execução com ambiente limpo. |
| Alta | Schedulers em múltiplas réplicas | APScheduler inicia no `lifespan` de cada processo FastAPI. | Garantir uma única instância executora dos jobs ou mover tarefas para worker/scheduler dedicado com coordenação. |
| Alta | Segredos e OAuth | Código lê arquivos de credenciais e token do Gmail e chaves do ambiente. | Armazenar segredos em secret manager/variáveis protegidas; não embutir OAuth files ou `.env` na imagem. Rotacionar credenciais de desenvolvimento. |
| Média | Persistência de token no frontend | O JWT administrativo é salvo em `localStorage`. | Avaliar risco de XSS e considerar cookie `HttpOnly`, `Secure` e `SameSite` com proteção CSRF apropriada. |
| Média | Evolução do schema | `database/001_schema.sql` é o schema versionado; não foi identificado sistema automático de migração na branch analisada. | Definir política de migrações incrementais, backup antes de alteração e testes de upgrade. |
| Média | Backup e restauração | Não foi identificado procedimento automatizado versionado de backup/restore. | Definir frequência, retenção, criptografia, responsável e teste periódico de restauração. |

## 3. Integrações e privacidade

### Gmail

- O cliente utiliza OAuth 2.0 com escopo `gmail.readonly`.
- Arquivos de credenciais e token devem permanecer fora do Git e de imagens Docker.
- A renovação do token depende do fluxo OAuth e do armazenamento seguro do refresh token.
- O job busca mensagens com uma query configurável (`GMAIL_QUERY`, padrão `newer_than:7d`) e limite (`GMAIL_MAX_RESULTS`, padrão 50).

### OpenRouter

- O fallback de IA transmite assunto e corpo do e-mail quando o parser heurístico não consegue extrair campos obrigatórios.
- A aplicação mascara e-mail, CPF e telefone em campos livres dos logs e reduz o remetente ao domínio, mas isso não remove os dados do prompt enviado ao provedor.
- Antes de produção, confirmar quais dados podem ser enviados, política de retenção e uso para treinamento, região/processamento e controles contratados.
- Falhas externas são registradas; não foi identificada uma fila persistente de retentativas no fluxo atual.

## 4. Banco e ciclo de vida

- `database/001_schema.sql` define as quatro tabelas atuais e as constraints centrais.
- A rotina de limpeza remove fisicamente eventos cuja data limite (data de término, se existir; caso contrário, data de início) é anterior à data local de referência.
- Os logs de extração sobrevivem à exclusão do evento com `event_id = NULL`; isso preserva rastreabilidade, mas não recupera o evento excluído.
- Favoritos são removidos em cascata quando usuário ou evento é excluído.
- Backups precisam considerar o caráter destrutivo da limpeza automática.

## 5. Infraestrutura e execução

### Docker Compose e Dockerfiles

Há uma divergência entre a configuração atual da aplicação e comentários/variáveis do Compose. Além disso, o healthcheck do Dockerfile do backend consulta um caminho não exposto pela API. O Compose deve ser executado somente após uma validação completa que inclua:

1. criação de `.env` com todas as variáveis efetivamente utilizadas;
2. inicialização do banco e aplicação do schema SQL;
3. autorização OAuth do Gmail, quando a extração for habilitada;
4. chamada ao endpoint de health check;
5. acesso do frontend à API a partir do navegador;
6. execução dos testes de integração no ambiente resultante.

### Escalonamento

Não escale a API horizontalmente mantendo o scheduler embutido em cada réplica sem mecanismo de exclusão mútua. `max_instances=1` limita concorrência dentro de um scheduler/processo, mas não coordena instâncias diferentes.

## 6. Checklist antes de publicar

- [ ] CORS restrito aos domínios reais.
- [ ] Autenticação e autorização de aluno implementadas para favoritos (ou funcionalidade desabilitada até lá).
- [ ] Fluxo de envio ao LLM revisado com responsável institucional por privacidade/dados.
- [ ] Segredos e tokens armazenados em mecanismo apropriado e fora das imagens.
- [ ] Healthcheck alinhado a uma rota existente.
- [ ] Docker Compose e variáveis de ambiente testados de ponta a ponta.
- [ ] Scheduler configurado para executar uma única vez por ciclo no ambiente implantado.
- [ ] Backups e procedimento de restauração documentados e testados.
- [ ] Migrações do banco e plano de rollback definidos.
- [ ] Testes backend, banco e frontend executados antes da publicação.
- [ ] Logs, métricas, alertas e política de retenção definidos.
- [ ] Credenciais administrativas iniciais e JWT secrets configurados fora do repositório.

## 7. Limite deste documento

Esta lista é uma análise estática da implementação consultada, não um pentest, auditoria jurídica, revisão de infraestrutura hospedada ou certificação de segurança. Revalidar os itens após cada alteração relevante e antes de qualquer publicação.
