# Migração do backend para PostgreSQL

Este documento registra **por que** o backend começou em SQLite, **o que mudou** para
ele passar a rodar (e ser testado) em PostgreSQL e **quais decisões** foram tomadas
no caminho, com os trade-offs. Para rodar tudo, vá direto para
[Como rodar](#como-rodar).

## 1. Como era (SQLite)

- `backend/app/core/config.py` usava `sqlite:///./eventos.db` como `DATABASE_URL` padrão
  e o `.env.example` dizia: *"SQLite local (padrão enquanto o PostgreSQL não está pronto)"*.
- `backend/app/database/database.py` tinha um ramo só para SQLite
  (`check_same_thread=False`).
- `backend/tests/conftest.py` criava um SQLite **em memória** e chamava
  `Base.metadata.create_all`, ou seja, os testes montavam as tabelas a partir dos
  **models do SQLAlchemy** e não a partir do `database/001_schema.sql`.
- O `database/001_schema.sql` e o seed já eram PostgreSQL e eram testados à parte por
  `python database/run_tests.py`.

Resultado: o banco "de verdade" (com CHECKs e chaves estrangeiras) e o banco que o
backend e os testes usavam eram **dois bancos diferentes**. O que passava nos testes
do backend podia falhar no PostgreSQL.

## 2. O schema do banco (`database/001_schema.sql`)

Cinco tabelas, com nomes do modelo relacional:

| Tabela | Observação |
|--------|-----------|
| `usuario` | `id_usuario`, `nome`, `email`, `senha_hash`, `nome_perfil`, `is_admin`, `dt_cadastro` |
| `extracao` | `id_extracao`, `message_id`, `thread_id`, `body_hash`, `prompt`, `json_output`, `status`... |
| `events` | `id_event`, `title`, `description`, `event_type`, `int_event_date`, `int_event_time`, `end_event_date`, `end_event_time`, `event_location`, `registration_link`, `status`, `origin`... |
| `favorito` | chave primária composta (`id_usuario`, `id_events`) |
| `email_associado` | chave primária composta (`id_extracao`, `id_evento`) |

Os nomes das colunas do banco **não são** os que o backend usa nos atributos
(`Event.date`, `Event.time`, `Event.location`...). Em vez de renomear o banco ou mudar
o código do backend inteiro, os models ganharam o nome real da coluna no primeiro
argumento do `mapped_column`:

```python
date: Mapped[dt.date] = mapped_column("int_event_date", Date)
```

O código dos repositórios, serviços e rotas **não muda**.

## 3. O que a migração encontrou (só aparece rodando em PostgreSQL)

| # | Problema | Onde aparecia | Correção |
|---|----------|---------------|----------|
| 1 | O backend **não subia em nenhum banco**: `favorites.user_id` apontava para uma tabela de usuários que não existia nos models. `create_all` levantava `NoReferencedTableError`. Na suíte completa isso quebrava 6 testes de extração. | `app/models/events/models.py` (US 6.1) | Novo `app/models/user.py` mapeando `usuario`; `Favorite` passa a mapear `favorito`. |
| 2 | Evento extraído de e-mail **sem link** (o parser devolve `""`) era recusado pelo CHECK `ck_events_registration_link_http`, quebrando a extração (US 4.1) em PostgreSQL. | `database/001_schema.sql` | O CHECK exige link `http(s)` só quando `origin = 'manual'`; para outras origens aceita vazio, mas link preenchido continua precisando ser `http(s)`. |
| 3 | `psycopg` (driver do PostgreSQL) não estava no `requirements.txt`; `pytest`, `pytest-mock` e `httpx` não estavam em nenhum arquivo, embora os testes dependam deles. | `backend/requirements.txt` | `psycopg[binary]` em `requirements.txt`; novo `requirements-dev.txt`. |
| 4 | **Apagar evento vindo de e-mail dava erro 500**: `extraction_logs.event_id` apontava para `events` sem regra de exclusão. O SQLite não fiscaliza chaves estrangeiras (por padrão), o PostgreSQL sim. Afetava `DELETE /events/{id}` (US 2.3) e a limpeza de expirados (US 5.1). | `app/models/extraction_log.py` (US 4.1) | `ForeignKey("events.id_event", ondelete="SET NULL")`: o log sobrevive com `event_id` nulo. Em banco que já tem a tabela: `ALTER TABLE extraction_logs DROP CONSTRAINT extraction_logs_event_id_fkey, ADD CONSTRAINT extraction_logs_event_id_fkey FOREIGN KEY (event_id) REFERENCES events(id_event) ON DELETE SET NULL;` ou recrie a tabela. |

## 4. O que mudou, arquivo por arquivo

| Arquivo | Mudança |
|---------|---------|
| `backend/app/core/config.py` | `DATABASE_URL` padrão passa a ser `postgresql+psycopg://postgres:dev@localhost:5432/eventos`. |
| `backend/.env.example` | Exemplo de `DATABASE_URL` em PostgreSQL e a ordem de preparação (schema antes do backend). |
| `backend/app/database/database.py` | Removido o ramo SQLite (`connect_args`); docstring atualizada. |
| `backend/app/main.py` | Importa o model `User`; comentários explicando por que `create_all` continua. |
| `backend/app/models/event.py` | Colunas mapeadas para os nomes do schema (`id_event`, `int_event_date`, `int_event_time`, `event_location`). |
| `backend/app/models/user.py` | **Novo.** Mapeia `usuario`. |
| `backend/app/models/events/models.py` | `Favorite` mapeia `favorito` (PK composta, sem `id`/`created_at`). |
| `backend/app/models/extraction_log.py` | `event_id` referencia `events.id_event` com `ON DELETE SET NULL` (item 4). |
| `backend/requirements.txt` | `psycopg[binary]==3.2.3`. |
| `backend/requirements-dev.txt` | **Novo.** `pytest`, `pytest-mock`, `httpx`. |
| `backend/tests/conftest.py` | Reescrito: cria o banco temporário `iesi_test_backend`, aplica `database/001_schema.sql`, completa com `create_all`, limpa **todas** as tabelas entre os testes e apaga o banco no fim. |
| `backend/tests/test_delete_evento_com_log.py` | **Novo.** Apagar evento extraído de e-mail mantém o log. |
| `database/001_schema.sql` | Regra do link (item 2). |
| `database/tests/001_schema_test.sql` | +3 verificações da regra do link. |
| `docs/migracao-postgresql.md` | Este documento. |

## 5. Decisões e trade-offs

### 5.1 Quem cria as tabelas: o SQL ou o `create_all`?

**Decisão:** o `database/001_schema.sql` é o dono de `usuario`, `extracao`, `events`,
`favorito` e `email_associado`. O `create_all` continua no `lifespan` do `main.py`, mas
só completa o que o SQL ainda não tem (`admins` e `extraction_logs`), porque o
SQLAlchemy não recria tabelas que já existem.

| | SQL cria (adotado) | `create_all` cria |
|---|---|---|
| Regras de negócio no banco (CHECK, FK, UNIQUE) | **Sim**: o backend não consegue gravar dado inválido, mesmo com bug | Não: o model não tem os CHECKs |
| Backend independente do script | Não: precisa rodar o SQL antes da primeira subida | Sim |
| Risco | Subir o backend antes do SQL cria tabelas sem regras (e o SQL falha com "já existe") | Regras duplicadas em dois lugares, tendendo a divergir |

Por que não remover o `create_all`: `admins` e `extraction_logs` são de outras tarefas
e não estão no SQL. Quando entrarem (ou forem substituídas por `usuario`/`extracao`), o
`create_all` pode sair.

### 5.2 Nomes do banco diferentes dos do backend

**Adotado:** mapear no model (nome real da coluna no primeiro argumento do
`mapped_column`), sem tocar em repositórios, serviços e rotas.
**Alternativa:** renomear as colunas do banco para os nomes do backend (como a equipe
havia combinado antes) — o código do backend não precisaria de mapeamento. Custo do
adotado: dois nomes para a mesma coisa (`Event.date` ↔ `int_event_date`). Se o time
preferir renomear o banco, basta remover os primeiros argumentos dos `mapped_column`.

### 5.3 Model `User` e `Favorite`

`User` é só um espelho de `usuario` (sem ele o backend não sobe, item 1). `Favorite`
perdeu `id` e `created_at` porque a tabela `favorito` não os tem; nenhum código usava
esses campos. Observação para o time: hoje coexistem `admins` (autenticação atual) e
`usuario` (modelo relacional).

### 5.4 Regra do link de inscrição

A US 2.1 exige link no cadastro manual, e o backend valida com `HttpUrl`. Já a
extração por e-mail (US 4.1) grava `registration_link = ""` quando o e-mail não traz URL
(a coluna é `NOT NULL`). O CHECK anterior (`http(s)` sempre) tornava a extração
impossível. A regra nova mantém o rigor onde o contrato exige. Alternativa descartada:
trocar o vazio por um link falso no parser (mexeria em código da US 4.1 e inventaria dado).

### 5.5 Testes: banco temporário versus transação por teste

**Adotado:** um banco temporário por execução do pytest + `TRUNCATE ... RESTART
IDENTITY CASCADE` antes de cada teste. É simples, isola os testes e permite testar
código que chama `commit()` (todos os repositórios chamam). A alternativa (transação
com rollback por teste) é mais rápida, mas exige tratar `commit()` dentro do código
testado. Custo atual: ~0,5 s por execução.

### 5.6 Fim do suporte a SQLite

Manter os dois bancos significaria manter dois comportamentos (tipos, constraints,
ordenação). O objetivo é o banco único em PostgreSQL, então o ramo SQLite foi
removido. Quem ainda tiver `eventos.db` local pode apagá-lo.

## 6. Pendências que não são desta migração (para o time decidir)

- `usuario` (modelo relacional) × `admins` (autenticação atual).
- `extracao` (SQL) × `extraction_logs` (backend, US 4.1): nomes e colunas diferentes;
  o backend usa `extraction_logs` e a tabela `extracao` fica sem uso por enquanto.
- `admins` e `extraction_logs` ainda dependem do `create_all`.
- `int_event_date` / `int_event_time` (início do evento): o `int_` provavelmente é
  `init_`; vale conferir o nome antes de congelar o schema.
- `Security.py` e `security.py` coexistem em `backend/app/core` (quebra no Windows/macOS).
- `ExtractionLog.extracted_data` recebe uma **string** JSON (`json.dumps`) numa coluna
  JSON: funciona, mas guarda texto em vez de objeto (US 4.1).
- Os índices da tabela `events` ainda serão adicionados (tarefa do banco); os testes
  deles entram junto.

## Como rodar

Pré-requisito: PostgreSQL 13+ rodando (usuário `postgres`, senha `dev` nos exemplos;
ajuste conforme a sua instalação).

```bash
# 1. dependências do backend e dos testes (na pasta backend)
pip install -r requirements-dev.txt

# 2. banco de desenvolvimento (uma vez), na raiz do repositório
psql -U postgres -c "CREATE DATABASE eventos"
psql -U postgres -d eventos -v ON_ERROR_STOP=1 -f database/001_schema.sql
psql -U postgres -d eventos -v ON_ERROR_STOP=1 -f database/002_seed_eventos.sql   # opcional: 20 eventos de teste

# 3. configuração: copie backend/.env.example para backend/.env e ajuste DATABASE_URL

# 4. subir a API (pasta backend)
uvicorn app.main:app --reload

# 5. testes
python database/run_tests.py          # banco: schema + seed (raiz do repositório)
python -m pytest backend              # backend em PostgreSQL (raiz do repositório)
```

Se o seu servidor não é `postgres:dev@localhost:5432`, defina `DATABASE_ADMIN_URL`
(usada por `run_tests.py` e pelo `conftest.py`) e `DATABASE_URL` (usada pela API). No
PowerShell: `$env:DATABASE_ADMIN_URL = "postgresql://usuario:senha@localhost:5432/postgres"`.
