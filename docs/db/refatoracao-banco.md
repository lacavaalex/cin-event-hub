# Refatoração do banco de dados: decisões e mudanças (v1.0)

Documento de mudanças do banco combinado na retrospectiva da Sprint 4 (30/10/2026): registra **o que mudou**, **por quê**, **o que ficou de fora** e **o que foi mexido em código de outras pessoas**. Complementa [`migracao-postgresql.md`](migracao-postgresql.md) (o backend em PostgreSQL) e [`paginacao-eventos.md`](paginacao-eventos.md) (IESI-71/70). Esses dois chegam à develop junto com a branch `refactor/banco-testes-seed` (ver o estado na seção 1).

**Fontes:** Backlog v3 (DoD D1–D10, riscos), Resumo da Sprint Planning 02, modelo relacional e EER do projeto, schema do José (`Banco-de-dados-completo`).
**Regra usada:** a user story manda; na falta dela, o modelo relacional/EER; na falta dos dois, a menor mudança que não quebra nada. Cada task só faz o que a própria task pede.

## 1. Linha do tempo

| Entrega | Quem | O que é | Situação |
|---------|------|---------|----------|
| IESI-56 / IESI-57 | Bruno | tabela de eventos e massa de 20 eventos (versão SQLite-era) | mescladas (#9, #10); **substituídas** pelo schema final do José |
| `Banco-de-dados-completo` | José | schema final de 5 tabelas, índices, seeds 002–006 | base do banco v1.0 |
| PR #17 `refactor/banco-testes-seed` | Bruno | `run_tests.py`, seed 002 e testes SQL adaptados ao schema de 5 tabelas; regra do link por origem | mesclado na branch do José (30/10) |
| PR #16 US 5.1/5.2 | Wallyson | expiração e limpeza de eventos | mesclado na develop depois das correções da revisão |
| PR #18 migração | Bruno | backend e testes em PostgreSQL, models mapeados ao schema | mesclado em `refactor/banco-testes-seed` |
| PR #19 IESI-71 | Bruno | LIMIT/OFFSET na consulta de eventos | mesclado em `refactor/banco-testes-seed` |
| PR #20 IESI-70 | Bruno | `GET /events` paginado | mesclado em `refactor/banco-testes-seed` (06/11) |
| `fix(database)` índice no teste | Bruno | `001_schema_test.sql` passa a esperar `uk_sucesso_de_extracao` (nome dado pelo José) | patch pronto; só é necessário quando os commits do José entrarem na develop (ver P1) |
| IESI-60 | Bruno | minimização de dados dos e-mails (LGPD) — ver [`lgpd-minimizacao-dados.md`](lgpd-minimizacao-dados.md) | este PR |

**Estado em 07/11/2026:** a `develop` termina no PR #16 e **ainda não tem** o banco do José nem a branch `refactor/banco-testes-seed` (que reúne #17–#20). Nenhum PR está aberto. A `Banco-de-dados-completo` do José tem 2 commits (seeds 003–006 e o índice renomeado) que a branch do Bruno não tem. A IESI-60 foi feita sobre a develop atual e não depende de nada disso. Quando o banco entrar, a ordem é: banco do José → `refactor/banco-testes-seed` → `fix(database)` do índice. Depois de cada merge, **apagar a branch** (combinado da Sprint 4).

## 2. Schema final (`database/001_schema.sql`)

| Tabela | Chave | Observações |
|--------|-------|-------------|
| `usuario` | `id_usuario` | `senha_hash`, `nome_perfil`, `is_admin`, `dt_cadastro`; e-mail único |
| `extracao` | `id_extracao` | `message_id`, `thread_id`, `body_hash` (64), `input_text`, `prompt`, `json_output` (JSONB), `status` (`pending/success/failed`); índice único parcial `uk_sucesso_de_extracao` (1 sucesso por mensagem+thread) |
| `events` | `id_event` | FK `extraction_id` e `admin_id` (`ON DELETE SET NULL`, no máximo um dos dois), CHECKs de título/descrição/local, tipo, link, status (`active/inactive`), capacidade, fim completo e fim ≥ início; índices por data, tipo e título |
| `favorito` | (`id_usuario`, `id_events`) | `ON DELETE CASCADE` nas duas FKs |
| `email_associado` | (`id_extracao`, `id_evento`) | `ON DELETE CASCADE` nas duas FKs |

## 3. Nomes: banco × backend

O banco manda nos nomes; o backend **não mudou os atributos Python**: os models passam o nome real da coluna no 1º argumento de `mapped_column`.

| Atributo Python | Coluna no banco |
|-----------------|-----------------|
| `Event.id` | `events.id_event` |
| `Event.date` / `Event.time` | `int_event_date` / `int_event_time` |
| `Event.end_date` / `Event.end_time` | `end_event_date` / `end_event_time` |
| `Event.location` | `event_location` |
| `User.id`, `name`, `hashed_password`, `profile_name`, `created_at` | `usuario.id_usuario`, `nome`, `senha_hash`, `nome_perfil`, `dt_cadastro` |
| `Favorite` | `favorito` (PK composta `id_usuario`, `id_events`) |
| `ExtractionLog.event_id` | FK para `events.id_event` com `ON DELETE SET NULL` |

## 4. Decisões

| # | Questão | Decisão | Por quê |
|---|---------|---------|---------|
| D1 | Quem cria as tabelas | **O SQL é a fonte** de `usuario`, `extracao`, `events`, `favorito`, `email_associado`. O `create_all` só completa `admins` e `extraction_logs`, que o SQL não tem | O schema tem CHECKs, índice parcial e identidades que o `create_all` não reproduz; regra de negócio no banco |
| D2 | Nomes das colunas ≠ nomes do backend | **Mapear nos models**, sem renomear o banco | Renomear quebraria o schema do José; mapear toca só os models e não muda repositórios, serviços nem rotas |
| D3 | `int_event_*` (provável typo de `init_`) | **Mantido** | Corrigir mudaria o arquivo do José sem combinar. O typo fica em 3 lugares: schema, seed e model |
| D4 | Link de inscrição obrigatório | `http(s)` obrigatório só para `origin = 'manual'`; outras origens aceitam `''` | US 2.1 exige link no cadastro manual; a US 4.1 só garante título, data, hora, local, tipo e descrição, e o parser grava `''` sem URL |
| D5 | Status `draft` (US 4.2) | **Descartado** | A US 4.4 trocou a curadoria por auto-publicação (`active`) e o código da develop já grava `active` |
| D6 | `extracao` (SQL) × `extraction_logs` (backend) | **Coexistem**; unificar é decisão em aberto. `extraction_logs.event_id` ganhou `ON DELETE SET NULL` | As US 4.3/4.4 dependem do log do backend; o `SET NULL` é necessário para apagar evento extraído de e-mail (PostgreSQL valida FK, o SQLite não) |
| D7 | `usuario` (SQL) × `admins` (login) | **Login continua em `admins`**; novo model `User` mapeia `usuario` (usado por `favorito`). Unificar depois | Trocar o login arriscaria a US 1.1 (Must) fora do escopo |
| D8 | `favorito` | **PK composta**, como no schema e no modelo relacional | — |
| D9 | Paginação (IESI-71/70) | `page` ≥ 1 (padrão 1), `page_size` 1–100 (padrão 20); resposta `{items, page, total_pages}`; `ORDER BY date, time, id`; página além do fim → 200 vazio | US 3.6 (20 por página) e US 3.1 (ordem cronológica); o `id` desempata |
| D10 | Front `eventService.js` | Uma linha: aceita lista ou `{items}` | A Home não quebra; paginação do front é a IESI-72 |
| D11 | Evento de vários dias expira no início ou no fim? | **No fim** (`COALESCE(end_date, date)`), granularidade de dia | US 5.1 fala em "data limite"; o schema tem `end_event_date`. **Já está na develop pelo PR #16**; só faltava mapear a coluna (ver 6) |
| D12 | `reference_date` no futuro em `POST /events/cleanup` | 422 | Com `2099-12-31` a rota apagava tudo. **Já corrigido no PR #16** |
| D13 | Fuso | `America/Recife` também nos testes | O CI em UTC falhava entre 21h e 24h. **Corrigido no PR #16** |
| D14 | Testes do backend | **Em PostgreSQL**: banco temporário `iesi_test_backend` com o `001_schema.sql` aplicado e tabelas limpas a cada teste | Testar em SQLite não exercitava CHECKs e FKs |
| D15 | Testes do banco | `python database/run_tests.py`: bancos temporários `iesi_test_*`, schema, seed e testes SQL | "npm test" do banco |

## 5. Como rodar os testes

Pré-requisito: PostgreSQL 13+ ligado (padrão `postgresql://postgres:dev@localhost:5432/postgres`; outro servidor: variável `DATABASE_ADMIN_URL`).

```powershell
python database/run_tests.py          # schema + seed (SQL puro)
cd backend
pip install -r requirements-dev.txt
python -m pytest                      # backend em PostgreSQL
```

Estado ao fechar este documento:

| Ambiente | `run_tests.py` | backend |
|----------|----------------|---------|
| develop atual (SQLite em memória) + IESI-60 | schema/seed antigos da develop | **111 passed, 1 skipped** (o skipped é o teste da IESI-60 que só vale com as tabelas `extracao`/`email_associado`) |
| develop + banco do José + #18–#20 + correção do índice + IESI-60 (PostgreSQL) | **74 verificações ok** | **144 passed** (sem `google-genai` instalado: 142 passed e 2 skipped) |

## 6. O que foi mexido em código de outras pessoas

Só o estritamente necessário, e nos pontos abaixo.

| Arquivo (dono) | Mudança | Por que foi necessário |
|----------------|---------|------------------------|
| `models/event.py` (Wallyson, IESI-32 e #16) | `end_date`/`end_time` passam a mapear `end_event_date`/`end_event_time` | O #16 declarou as colunas sem o nome real; em PostgreSQL falha o `INSERT` (36 testes quebravam) |
| `models/user.py` (Wallyson, #16: tabela `users`) | vale a versão da migração (`usuario`) | O schema do José chama a tabela `usuario`; é a regra D16 do comentário do PR #16 |
| `models/extraction_log.py` (Alex, US 4.1) | `ForeignKey(..., ondelete="SET NULL")` e, na IESI-60, só um comentário | Apagar evento extraído de e-mail dava 500 em PostgreSQL |
| `services/extracao_email/extraction_service.py` (Alex, US 4.1; US 4.2/4.4 de outros) | `_log`/`_short` aplicam a minimização (IESI-60) | É o único ponto que grava o log de extração |
| `requirements.txt` (vários) | `psycopg[binary]` junto de `google-genai` | O backend precisa do driver do PostgreSQL |
| `tests/conftest.py` (Alex, US 4.1) | reescrito para PostgreSQL | Testes passam a usar o schema oficial |
| `database/tests/*`, `database/run_tests.py`, `002_seed_eventos.sql` (Bruno, sobre o schema do José) | adaptados ao schema de 5 tabelas | Pedido do José antes do PR dele |
| `database/001_schema.sql` (José) | regra do link por origem (D4) | US 4.1 gravava `''` e o CHECK recusava; combinado com ele no PR #17 |

## 7. Pendências e mudanças estruturais que ficaram de fora

Combinado da Sprint 4: o que não entra agora fica documentado para o time avaliar no back-end.

| # | Pendência | Observação |
|---|-----------|-----------|
| P1 | `database/run_tests.py` vai falhar quando a `Banco-de-dados-completo` do José entrar | O José renomeou o índice para `uk_sucesso_de_extracao` e o teste ainda espera `sucesso_de_extracao`; a falha interrompe o teste do schema e esconde as verificações seguintes. Correção de 1 linha em `database/tests/001_schema_test.sql` (patch `fix(database)` pronto): com ela, **74 verificações ok**. Hoje, sem os commits do José, o teste passa como está |
| P2 | Seeds 003–006 (extrações, usuários, favoritos, e-mails associados) do José **não passam pelo `run_tests.py`** | Só o 002 é testado |
| P3 | Índices de `events` (`data_evento`, `tipo_evento`, `titulo_evento`) e CHECK `ck_events_criador_unico` não têm verificação | Acrescentar em `pg_indexes` / teste de CHECK |
| P4 | `database/.DS_Store` versionado | Remover e ignorar no `.gitignore` da raiz (hoje só o `frontend/.gitignore` ignora) |
| P5 | Unificar `extracao` com `extraction_logs` e `usuario` com `admins` (D6, D7) | Mudança estrutural; avaliar no back-end |
| P6 | `requirements.txt` fixa `pydantic[email]==2.9.2`, mas `google-genai==2.30.1` (US 4.2) exige `pydantic>=2.12.5` | `pip install -r requirements.txt` falha do zero; dono da US 4.2 precisa resolver |
| P7 | Home do PR #14 pagina no navegador sobre `getEvents()` | Com a API paginada ela só vê os 20 primeiros eventos; é a IESI-72 |
| P8 | `Security.py` e `security.py` versionados juntos em `backend/app/core/` | Colide em Windows/macOS (mesmo nome sem diferenciar maiúsculas); manter só um |
| P9 | Mascarar também a descrição publicada do evento (LGPD) | Decisão L2 em [`lgpd-minimizacao-dados.md`](lgpd-minimizacao-dados.md) |
