# CIn Event Hub

Plataforma web para centralização, extração automática via e-mail/IA e divulgação de eventos acadêmicos do Centro de Informática da UFPE (CIn/UFPE).

## Arquitetura

- **Banco de Dados (`database/`):** PostgreSQL 16 (Neon em produção) com schema relacional oficial (`001_schema.sql`), seeds idempotentes e suíte automatizada de integridade (`database/run_tests.py`).
- **Backend (`backend/`):** FastAPI + SQLAlchemy 2 + psycopg 3 + APScheduler, com autenticação JWT de administradores, CRUD de eventos, favoritos, limpeza automática de eventos expirados (`America/Recife`, UTC-3) e pipeline de extração de e-mails (Gmail API + parser estruturado + fallback via OpenRouter + validação autônoma + desduplicação de lembretes).
- **Frontend (`frontend/`):** React 19 + Vite + React Router, com tema claro/escuro, faixa "Esta semana", busca, filtros por tipo, exportação para agenda (`.ics`/Google Calendar), favoritos do navegador e painel administrativo completo.

## Execução Local com Docker

1. Crie `backend/.env` a partir de `backend/.env.example` preenchendo `DATABASE_URL`, `POSTGRES_PASSWORD`, `SECRET_KEY` (mínimo 32 caracteres) e, opcionalmente, `ADMIN_EMAIL`, `ADMIN_PASSWORD` e `OPENROUTER_API_KEY`.
2. Suba os serviços a partir da raiz do repositório:

```bash
docker compose --env-file backend/.env up -d --build
```

- Frontend: `http://localhost:5173`
- Backend / Swagger: `http://localhost:8000/docs` (healthcheck em `GET /health`)

## Execução Manual (Desenvolvimento)

### Banco e Backend
```bash
# Aplicar schema oficial no PostgreSQL
psql -U postgres -d cin_event_hub -v ON_ERROR_STOP=1 -f database/001_schema.sql

# Subir API
cd backend
python -m venv .venv
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm ci
cp .env.example .env
npm run dev
```

## Testes Automatizados

```bash
# 1. Banco de dados (requer PostgreSQL acessível via DATABASE_ADMIN_URL)
python database/run_tests.py

# 2. Backend (PostgreSQL temporário + cobertura de rotas, regras e serviços)
pytest backend

# 3. Frontend (testes unitários, lint e build de produção)
cd frontend && npm test && npm run lint && npm run build
```
