# Relatório Completo de Auditoria & Testes Ponta a Ponta — `cin-event-hub`

**Data/Hora:** 26/11/2026 às 14:25 (`America/Recife`, UTC-3)  
**Branch auditada:** `origin/develop` (`9668957` — *Merge pull request #30 from lacavaalex/feat/Dockerização-Deploy*)  
**Branch `origin/main`:** `1f204d9` (*chore: estrutura inicial do projeto (3 camadas)* — apenas `.gitkeep`)  
**PR aberto monitorado:** PR #32 (`feat/frontend-extracao-temas-hardening`, por Erlon Matheus)  
**URL de produção (Homepage do GitHub):** `https://cin-event-hub-frontend.vercel.app` *(retornando 404)*  
**URL de Preview ativa (branch `develop`, auditada no Chrome):** `https://cin-event-hub-frontend-56flrj208-alex-df2b.vercel.app/`  
**Backend em produção (Render):** `https://cin-event-hub.onrender.com`

---

## 1. Resumo Executivo (Placar das 7 Camadas)

| Camada | Status | Resultado Observado | Diagnóstico |
|---|---|---|---|
| **1. Banco de Dados (`database/run_tests.py`)** | ✅ **PASSOU** | **107/107 verificações ok** (3/3 etapas) | Schema, seeds, fuso UTC-3 e novo status `ignorado_duplicata` (US 4.5) 100% íntegros. |
| **2. Backend (`pytest backend`)** | ❌ **FALHOU** | **322 passed, 2 failed** (59 warnings) | 2 regressões introduzidas pelos merges dos PRs #27 e #30 (mais 1 falso positivo). |
| **3. E2E HTTP ao vivo local (PG + Uvicorn)** | ✅ **PASSOU** | **19/19 cenários passaram** | API local (Auth, CRUD, Unicode, Favoritos, Limpeza, Status extração, CORS, validações) saudável. |
| **4. Backend em Produção (Render)** | ✅ **ONLINE** (com 2 ressalvas) | `GET /` e `/events` **200**, `/events/admin` e `/extraction/status` **403** | API real respondendo e protegida, mas `GET /health` dá **404** (`BUG-02`) e CORS envia `*` + `credentials: true` (`BUG-04`). |
| **5. Frontend local (`test`, `lint`, `build`)** | ⚠️ **PARCIAL** | **9/9 testes**, `0` lint, build ok | Build e testes passam, mas há bugs visuais/integração (`EventCard` título duplicado, sem `FavoriteButton`, `FavoritesPage` estática). |
| **6. Docker & Deploy (PR #30)** | ❌ **QUEBRADO** | **6 falhas críticas/altas** | `HEALTHCHECK /health` 404, sem `001_schema.sql` no compose, envs desalinhadas e `dockerignore` sem ponto. |
| **7. Frontend na Vercel (Inspeção ao vivo)** | ⚠️ **PARCIAL / FALHAS S1** | Preview `/` **200** + integrado ao Render; **404 em F5/rotas diretas** e **404 no domínio principal** | Navegação SPA via clique funciona sem erros de console, mas F5/link direto em `/eventos/1`, `/favorites`, `/login` dá **404**; domínio oficial dá **404**; título duplicado no card; sem botão de favoritar. |

> [!WARNING]
> **Veredito geral:** O site na URL de preview da Vercel (`cin-event-hub-frontend-56flrj208-alex-df2b.vercel.app`) **está no ar e integrado ao backend real no Render (`cin-event-hub.onrender.com`)**, com busca, filtros, faixa "Esta semana", detalhes e "Adicionar à Agenda" funcionando via navegação interna. Porém, há **falhas críticas de deploy** (domínio principal da Vercel dando 404, F5/links diretos dando 404 por falta de `vercel.json`, Docker quebrado no PR #30), **2 testes falhando no `pytest`**, **2 bugs altos de UI** (título duplicado no card e ausência do botão de favoritar) e **1 item de segurança (`BUG-07`) tratado fora do repositório**.

---

## 2. O Que Mudou Desde a Última Auditoria (`c131e9d` → `9668957`)

1. **PR #31 (`fix/fuso-horario-recife`, mergeado em `c131e9d`):** ✅ **100% aprovado.** Datas em `America/Recife` (UTC-3) no banco, backend e `EventForm.jsx` passaram em todas as camadas.
2. **PR #27 (`feature/us-4.5-verificar-duplicacao`, mergeado em `fc9b3d7`):** ⚠️ **Implementação sólida, 1 teste quebrado no merge.** A lógica de desduplicação em [texto.py](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/app/core/texto.py), [event_repository.py](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/app/repositories/event_repository.py) e [extraction_service.py](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/app/services/extracao_email/extraction_service.py) está limpa e validada, mas `test_parser_tambem_interrompe_lembrete_duplicado` manteve a data antiga `2025-11-25` enquanto `EMAIL_OK` passou a usar `25/11/2030`.
3. **PR #30 (`feat/Dockerização-Deploy`, mergeado em `9668957`):** ❌ **Concentra a maioria dos defeitos.** Adicionou `docker-compose.yml`, `Dockerfile`s, `nginx.conf`, migrou `GeminiClient` para OpenRouter (`openai`), adicionou `logo2.ico` e 2 PDFs — porém sem sincronizar com o código real do backend, sem atualizar `test_gemini_client.py` e deixando um `main.py` protótipo na raiz.

---

## 3. Catálogo de Defeitos e Ações Necessárias

### 🔴 S1 — Críticos (Bloqueiam Produção, Docker ou CI)

#### `BUG-01` — Vercel: F5 / acesso direto retorna HTTP 404 em todas as subrotas + domínio oficial fora do ar
- **URLs verificadas ao vivo:**
  - **Preview ativa (`develop`):** `https://cin-event-hub-frontend-56flrj208-alex-df2b.vercel.app/`
    - `GET /` → **200 OK**, integra com `https://cin-event-hub.onrender.com/events?page_size=100` (**200 OK**), exibe 1 evento real (`"Palestra de Cybersecurity"`, `27/11/2026 14:00`), busca, filtros, detalhes e "Adicionar à Agenda" funcionando via clique interno (0 erros de console).
    - **FALHA no hard reload / link compartilhado:**
      - `GET /eventos/1` → **404 `NOT_FOUND`** (Vercel)
      - `GET /favorites` → **404 `NOT_FOUND`** (Vercel)
      - `GET /login` → **404 `NOT_FOUND`** (Vercel)
  - **Domínio oficial (Homepage do GitHub):** `https://cin-event-hub-frontend.vercel.app/` → **404 `NOT_FOUND`** inclusive na raiz `/` (provavelmente porque a **Production Branch** da Vercel aponta para `main`, que ainda só tem arquivos `.gitkeep` do commit `1f204d9`).
- **Como corrigir:**
  1. Criar `frontend/vercel.json`:
     ```json
     {
       "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
     }
     ```
  2. No painel da Vercel (`Settings → Git`): alinhar a **Production Branch** para `develop` (ou abrir PR de release `develop → main`) e garantir **Root Directory = `frontend`** para que a URL oficial `https://cin-event-hub-frontend.vercel.app` sirva a aplicação.

---

#### `BUG-02` — `backend/Dockerfile` tem `HEALTHCHECK` apontando para `/health` (HTTP 404)
- **Arquivos:** [backend/Dockerfile](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/Dockerfile#L47-L48) vs [backend/app/main.py](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/app/main.py#L101-L104)
- **Evidência:** O `Dockerfile` testa `http://localhost:8000/health`, mas `backend/app/main.py` expõe apenas `GET /` (`health_check()`). Toda checagem de saúde recebe **404**, marcando o container como **`unhealthy`** no Docker e falhando o deploy no Render/Railway.
- **Como corrigir:** Adicionar rota `@app.get("/health", tags=["health"])` em [backend/app/main.py](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/app/main.py) (mantendo `GET /` para compatibilidade) **ou** apontar o `HEALTHCHECK` para `http://localhost:8000/`. Recomenda-se expor `/health` no backend (boa prática para Render/Railway).

---

#### `BUG-03` — `docker-compose.yml` não aplica `database/001_schema.sql` no PostgreSQL
- **Arquivo:** [docker-compose.yml](https://github.com/lacavaalex/cin-event-hub/blob/develop/docker-compose.yml#L25-L37)
- **Evidência:** O serviço `db` monta apenas o volume `db_data:/var/lib/postgresql/data`, sem montar `./database/001_schema.sql` em `/docker-entrypoint-initdb.d/`.
- **Impacto:** Ao subir com `docker compose up`, as tabelas são criadas pelo `Base.metadata.create_all()` do SQLAlchemy **sem nenhuma das constraints `CHECK` e `ON DELETE` do schema oficial** (`ck_events_event_type`, `ck_events_registration_link_http`, `ck_extracao_status`, `ck_usuario_nome_preenchido`, etc.).
- **Como corrigir:** Montar o schema no serviço `db`:
  ```yaml
  volumes:
    - db_data:/var/lib/postgresql/data
    - ./database/001_schema.sql:/docker-entrypoint-initdb.d/001_schema.sql:ro
  ```

---

#### `BUG-04` — Desalinhamento crítico de variáveis de ambiente entre `docker-compose.yml`, `config.py`, `main.py` e `gemini_client.py`
- **Arquivos:** [docker-compose.yml](https://github.com/lacavaalex/cin-event-hub/blob/develop/docker-compose.yml#L64-L87), [backend/app/core/config.py](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/app/core/config.py#L44-L48), [backend/app/main.py](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/app/main.py#L87-L93), [backend/app/services/ia_gemini/gemini_client.py](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/app/services/ia_gemini/gemini_client.py#L43-L47)
- **Evidências:**
  1. **IA / OpenRouter:** `docker-compose.yml` passa apenas `GEMINI_API_KEY` e **não passa** `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL` nem `GEMINI_MODEL`. Enquanto isso, `config.py` define `GEMINI_MODEL` padrão como `"gemini-3.8-flash"` (sem prefixo `google/` e sem `:free`) — o próprio PDF da equipe alerta que isso gera `Error code: 400 - not a valid model ID` no OpenRouter!
  2. **Gmail:** `docker-compose.yml` passa `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN` (com comentário admitindo não ter verificado o código), mas o backend usa `GMAIL_CREDENTIALS_FILE` e `GMAIL_TOKEN_FILE` (arquivos JSON montados via volume ou secret).
  3. **CORS:** `docker-compose.yml` passa `ALLOWED_ORIGINS`, mas `backend/app/main.py` ignora totalmente e mantém `allow_origins=["*"]` hardcoded (e com `allow_credentials=True`, o que em navegadores modernos pode gerar conflito com credenciais).
  4. **Admin/JWT/Jobs:** `docker-compose.yml` não repassa `SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `EXTRACTION_ENABLED`, `CLEANUP_ENABLED`.
  5. **Caminho do `.env`:** o comentário no topo de `docker-compose.yml` diz para colocar `.env` na raiz (`veja .env.example`), mas só existe `backend/.env.example`, contradizendo o PDF que manda usar `--env-file backend/.env`.
- **Como corrigir:**
  - Ler `ALLOWED_ORIGINS`, `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL` e corrigir o default de `GEMINI_MODEL` (`google/gemma-4-31b-it:free`) em [backend/app/core/config.py](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/app/core/config.py) e aplicar `ALLOWED_ORIGINS` em [backend/app/main.py](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/app/main.py).
  - Atualizar `environment:` de `backend` em [docker-compose.yml](https://github.com/lacavaalex/cin-event-hub/blob/develop/docker-compose.yml) com `env_file: ./backend/.env` (sobrescrevendo apenas `DATABASE_URL` para apontar para `@db:5432`) e remover as 3 variáveis fictícias de Gmail.

---

#### `BUG-05` — Falha no `pytest`: `test_gemini_client.py` quebrado após migração para OpenRouter (e 1 falso positivo)
- **Arquivos:** [backend/tests/test_gemini_client.py](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/tests/test_gemini_client.py#L117-L151), [backend/app/services/ia_gemini/gemini_client.py](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/app/services/ia_gemini/gemini_client.py#L67-L106), [backend/requirements.txt](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/requirements.txt#L14-L15)
- **Evidência observada:**
  - `FAILED backend/tests/test_gemini_client.py::test_generate_chama_sdk_e_retorna_texto`
  - O PR #30 migrou `GeminiClient._generate()` do SDK `google-genai` para `openai.OpenAI` (OpenRouter), mas **não atualizou os testes** `test_generate_chama_sdk_e_retorna_texto` e `test_generate_encapsula_erro_do_sdk`, que continuam fazendo `pytest.importorskip("google.genai")` e `monkeypatch.setattr(genai, "Client", _Client)`.
  - Mesmo com `openai` instalado, `test_generate_chama_sdk_e_retorna_texto` **tenta chamar a internet real** (`https://openrouter.ai/api/v1`) com `api_key="teste"` e falha; já `test_generate_encapsula_erro_do_sdk` passa por **falso positivo** (captura erro de import/rede em vez da exceção simulada pelo mock!).
  - Além disso, `google-genai==2.30.1` continuou em `backend/requirements.txt` sem ser usado em nenhum lugar do código (aumentando peso da imagem Docker desnecessariamente).
- **Como corrigir:**
  1. Atualizar os dois testes em [test_gemini_client.py](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/tests/test_gemini_client.py#L117-L151) para mockar `openai.OpenAI` (verificando `base_url`, `api_key`, `model`, `choices[0].message.content` e propagação de exceção).
  2. Remover `google-genai==2.30.1` de [backend/requirements.txt](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/requirements.txt) e instalar `openai>=1.50.0` nos ambientes locais/CI.

---

#### `BUG-06` — Falha no `pytest`: `test_extraction_service.py::test_parser_tambem_interrompe_lembrete_duplicado`
- **Arquivo:** [backend/tests/test_extraction_service.py](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/tests/test_extraction_service.py#L51-L57) e [linhas 386–399](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/tests/test_extraction_service.py#L386-L399)
- **Evidência observada:**
  - `AssertionError: assert 1 == 0` (`summary.processed == 1`, `reminders_ignored == 0`).
- **Causa raiz:** `EMAIL_OK` (linha 51) foi atualizado no PR #29 para `"Palestra de Segurança 2030\nData: 25/11/2030"`, mas o teste `test_parser_tambem_interrompe_lembrete_duplicado` (vindo do PR #27) cria `_evento_ativo(..., "Palestra de Segurança 2026", data=dt.date(2025, 11, 25))`. Como as datas não batem (`2025-11-25` ≠ `2030-11-25`), a duplicata não é detectada.
- **Como corrigir:** Atualizar o teste (linhas 389–392) para usar `"Palestra de Segurança 2030"` e `data=dt.date(2030, 11, 25)` (alinhado ao `EMAIL_OK`).

---

### 🟠 S2 — Altos (Segurança, Vazamento de Dados e Integração Frontend)

#### `BUG-07` — Segurança
- Item de segurança tratado fora do repositório; detalhes omitidos deste documento.

---

#### `BUG-08` — `backend/dockerignore` e `frontend/dockerignore` sem ponto inicial (`.dockerignore`)
- **Arquivos:** [backend/dockerignore](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/dockerignore) e [frontend/dockerignore](https://github.com/lacavaalex/cin-event-hub/blob/develop/frontend/dockerignore)
- **Impacto:** O Docker **ignora completamente** arquivos chamados `dockerignore` sem o ponto inicial. Com isso, `COPY . .` envia `.env`, `.venv/`, `gmail_token.json`, `gmail_credentials.json`, `__pycache__/` e `node_modules/` para dentro do build/imagem (risco de vazamento de segredos na imagem Docker + build lentíssimo).
- **Como corrigir:** Renomear via `git mv` para `backend/.dockerignore` e `frontend/.dockerignore` (e adicionar `gmail_token*.json`, `gmail_credentials*.json`, `*.pem`, `*.key` em `backend/.dockerignore`).

---

#### `BUG-09` — Arquivo órfão/quebrado `main.py` na raiz do repositório
- **Arquivo:** [main.py](https://github.com/lacavaalex/cin-event-hub/blob/develop/main.py)
- **Evidência:** Importa `from app.api.favoritos.router import router as favoritos_router` (módulo que não existe!), possui `TODO` antigo do IESI-29 e não tem `lifespan`, `auth`, `extraction` nem `cleanup`. Foi commitado por engano no PR #30.
- **Como corrigir:** Remover `main.py` da raiz (`git rm main.py`), migrando apenas a leitura de `ALLOWED_ORIGINS` e a rota `/health` para [backend/app/main.py](https://github.com/lacavaalex/cin-event-hub/blob/develop/backend/app/main.py).

---

#### `BUG-10` — Frontend `FavoritesPage.jsx` estática e `X-User-Id: "1"` hardcoded em `eventsApi.js`
- **Arquivos:** [FavoritesPage.jsx](https://github.com/lacavaalex/cin-event-hub/blob/develop/frontend/src/pages/FavoritesPage.jsx), [eventsApi.js](https://github.com/lacavaalex/cin-event-hub/blob/develop/frontend/src/services/eventsApi.js#L59-L71)
- **Evidência:**
  - `FavoritesPage.jsx` exibe sempre o texto fixo `"Você ainda não tem eventos favoritos"` e **não chama** `GET /events/favorites` (já implementado no backend na US 6.2!).
  - `eventsApi.js` fixa `X-User-Id: "1"` (não usa o `anonymousUserId` nem sessão de usuário), falhando com 404 se não houver usuário `id=1` no banco, e todos os visitantes compartilham o mesmo usuário `1`.
- **Como corrigir:** Integrar `FavoritesPage.jsx` com `GET /events/favorites` e alinhar a estratégia de identificação de usuário entre frontend e backend (usuário padrão/anônimo ou autenticação de aluno).

---

#### `BUG-11` — `VITE_API_URL` sem fallback em `authService.js`/`eventService.js` e `frontend/.env.example` apontando para porta `3000` + mock ativo
- **Arquivos:** [authService.js](https://github.com/lacavaalex/cin-event-hub/blob/develop/frontend/src/services/authService.js#L1), [eventService.js](https://github.com/lacavaalex/cin-event-hub/blob/develop/frontend/src/services/eventService.js#L3), [eventsApi.js](https://github.com/lacavaalex/cin-event-hub/blob/develop/frontend/src/services/eventsApi.js#L1), [frontend/.env.example](https://github.com/lacavaalex/cin-event-hub/blob/develop/frontend/.env.example)
- **Evidência:**
  - Se o frontend for buildado (ex.: na Vercel) sem `VITE_API_URL` definida, `authService.js` e `eventService.js` disparam requisições para `undefined/auth/login` e `undefined/events`.
  - Se `VITE_API_URL` terminar com `/`, gera URLs com barra dupla (`//events`).
  - `frontend/.env.example` na `develop` ainda tem `VITE_API_URL=http://localhost:3000` e `VITE_USE_MOCK=true` (porta errada — backend é `8000`). *(Nota: PR #32 já corrige `.env.example` para `8000`.)*
- **Como corrigir:** Centralizar `API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/+$/, "")` em um único módulo compartilhado pelos 3 serviços.

---

#### `BUG-19` — Bug visual ao vivo na Home: título do evento renderizado em duplicidade no `EventCard.jsx`
- **Arquivo:** [EventCard.jsx](https://github.com/lacavaalex/cin-event-hub/blob/develop/frontend/src/components/EventCard.jsx#L22-L25)
- **Evidência ao vivo na Vercel:** Cada card na Home exibe **um link roxo sublinhado sem estilo** `<a href="/eventos/1">Palestra de Cybersecurity</a>` e logo abaixo `<h3 class="event-title">Palestra de Cybersecurity</h3>`, duplicando o título na tela.
- **Causa raiz:** As linhas 23–24 renderizam `<Link>` e `<h3>` como irmãos em vez de colocar `<Link>` dentro do `<h3>` (ou estilizar o link).
- **Como corrigir:** Envolver o `<Link>` dentro de `<h3 className="event-title">` (e aplicar `text-decoration: none; color: inherit` no CSS).

---

#### `BUG-20` — Botão de favoritar ausente na interface (`EventCard.jsx` e `EventDetails.jsx`)
- **Arquivos:** [FavoriteButton.jsx](https://github.com/lacavaalex/cin-event-hub/blob/develop/frontend/src/components/events/FavoriteButton.jsx), [EventCard.jsx](https://github.com/lacavaalex/cin-event-hub/blob/develop/frontend/src/components/EventCard.jsx), [EventDetails.jsx](https://github.com/lacavaalex/cin-event-hub/blob/develop/frontend/src/pages/EventDetails.jsx)
- **Evidência ao vivo na Vercel:** O cabeçalho mostra `Meus Favoritos`, mas **não existe nenhum botão/estrela de favoritar** nem nos cards da Home nem na página de detalhes `/eventos/1` — `FavoriteButton.jsx` nunca é importado em nenhum componente.
- **Como corrigir:** Renderizar `<FavoriteButton>` em `EventDetails.jsx` (e opcionalmente em `EventCard.jsx`) integrado à mesma identificação de usuário usada em `FavoritesPage.jsx` (`BUG-10`).

---

### 🟡 S3 — Médios (Compatibilidade, Contrato e Atenção ao PR #32)

#### `BUG-12` — `frontend/Dockerfile` usa `node:20-slim` com Vite 8 (`node: ^20.19.0 || >=22.12.0`)
- **Arquivo:** [frontend/Dockerfile](https://github.com/lacavaalex/cin-event-hub/blob/develop/frontend/Dockerfile#L14)
- **Detalhes:** `vite@8.3.1` exige `^20.19.0 || >=22.12.0`. Usar `FROM node:22-slim AS build` evita quebra em caches antigos de `node:20-slim`.

#### `BUG-13` — Filtro `Minicurso` inexistente no backend + paginação client-side na `Home.jsx`
- **Arquivos:** [eventService.js](https://github.com/lacavaalex/cin-event-hub/blob/develop/frontend/src/services/eventService.js#L133-L139), [Home.jsx](https://github.com/lacavaalex/cin-event-hub/blob/develop/frontend/src/pages/Home.jsx#L26)
- **Detalhes:** O chip `Minicurso` nunca retornará resultados reais do PostgreSQL (o `CHECK` do banco só permite `Palestra`, `Workshop`, `Hackathon`, `Outro`). Além disso, `Home.jsx` pede `pageSize: 100` e pagina no cliente — se houver > 100 eventos ativos, os demais ficam invisíveis.

#### `BUG-14` — `ExtractionStatusPage.jsx` ainda é placeholder na `develop`
- **Arquivo:** [ExtractionStatusPage.jsx](https://github.com/lacavaalex/cin-event-hub/blob/develop/frontend/src/pages/ExtractionStatusPage.jsx)
- **Status:** Já implementado no **PR #32 aberto** (`feat/frontend-extracao-temas-hardening`).

#### `BUG-15` — ⚠️ Alerta crítico ANTES de mergear o PR #32 (`feat/frontend-extracao-temas-hardening`)
- **O que o PR #32 melhora:** remove o arquivo problemático `backend/app/core/Security.py`, implementa `ExtractionStatusPage.jsx` (US 4.3), adiciona tema claro/escuro e corrige `frontend/.env.example`.
- **O que vai quebrar se mergear como está:**
  - `backend/app/core/config.py` no PR #32 lança `RuntimeError` **no momento do `import`** se `DATABASE_URL` estiver vazia ou se `SECRET_KEY` tiver menos de 32 caracteres — isso vai **quebrar toda a suíte `pytest backend`** (pois `conftest.py` importa `app.database.Base` sem setar `DATABASE_URL`/`SECRET_KEY` no ambiente) e quebrará os testes de `_seed_admin` (`test_roteiro_wallyson.py`) se não houver fixtures/env de teste configurados em `conftest.py`.

#### `BUG-16` — `README.md` na raiz está vazio (0 bytes) e `Security.py` ainda suja `git status` no Windows
- **Arquivos:** [README.md](https://github.com/lacavaalex/cin-event-hub/blob/develop/README.md), `backend/app/core/Security.py`
- **Ação:** Preencher `README.md` com visão geral, link da aplicação e instruções corretas de setup/Docker/testes; aceitar a remoção de `Security.py` (já presente no PR #32).

---

### 🟢 S4 — Baixos / Polimento

- **`BUG-17` — [frontend/index.html](https://github.com/lacavaalex/cin-event-hub/blob/develop/frontend/index.html#L2-L5):** `<html lang="en">` em aplicação em português (`pt-BR`) e `<link rel="icon" type="image/svg+xml" href="/logo2.ico" />` com MIME type incorreto (`image/x-icon`).
- **`BUG-18` — Warnings no `pytest` (59 warnings):** `python-jose` usa `datetime.utcnow()` depreciado no Python 3.12 e `passlib` loga erro ao ler `bcrypt.__about__`. Não quebra execução hoje, mas vale acompanhar.
- **`BUG-21` — Aviso DOM no `/login`:** Chrome reporta falta do atributo `autocomplete="current-password"` no `<input type="password">` em [Login.jsx](https://github.com/lacavaalex/cin-event-hub/blob/develop/frontend/src/pages/Login.jsx).

---

## 4. Plano de Ação Priorizado para a Equipe

| Prioridade | Ação | Bugs resolvidos |
|---|---|---|
| **P0 (Imediato — Segurança)** | Item tratado fora do repositório | `BUG-07` |
| **P0 (Imediato — Produção)** | Adicionar `frontend/vercel.json` (rewrite SPA para acabar com 404 no F5/link direto) e corrigir **Production Branch / Root Directory** na Vercel para ativar o domínio oficial `cin-event-hub-frontend.vercel.app` | `BUG-01`, `BUG-11` |
| **P0 (Imediato — CI Verde)** | Corrigir os 2 testes quebrados (`test_extraction_service.py` data `2030` + `test_gemini_client.py` mock do `openai.OpenAI`) e remover `google-genai` não utilizado | `BUG-05`, `BUG-06` |
| **P1 (Docker Funcional)** | Expor `GET /health` (também hoje 404 no Render) e ler `ALLOWED_ORIGINS` em `backend/app/main.py`; montar `001_schema.sql` e alinhar variáveis no `docker-compose.yml`; renomear `.dockerignore`; remover `main.py` da raiz; atualizar `frontend/Dockerfile` para `node:22-slim` | `BUG-02`, `BUG-03`, `BUG-04`, `BUG-08`, `BUG-09`, `BUG-12` |
| **P1 (UI Ao Vivo + PR #32)** | Corrigir título duplicado em `EventCard.jsx`; ajustar `conftest.py` no PR #32 para não quebrar `pytest` sem `.env` | `BUG-14`, `BUG-15`, `BUG-16`, `BUG-19` |
| **P2 (Sprint/Entrega)** | Adicionar `<FavoriteButton>` na UI e conectar `FavoritesPage.jsx` ao `GET /events/favorites` sem `X-User-Id: 1` fixo; remover chip `Minicurso` (ou alinhar enum); preencher `README.md`; ajustar `index.html` e `autocomplete` no login | `BUG-10`, `BUG-13`, `BUG-16`, `BUG-17`, `BUG-20`, `BUG-21` |

---

