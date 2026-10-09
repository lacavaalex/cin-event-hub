"""Ponto de entrada da aplicação FastAPI — CIn Event Hub Backend.

Ao iniciar:
1. Cria as tabelas no banco (SQLite / PostgreSQL) se não existirem.
2. Gera o admin seed se a tabela estiver vazia (credenciais no .env).
3. Registra os routers de autenticação e eventos.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth.router import router as auth_router
from app.api.eventos.router import router as events_router
from app.core.config import ADMIN_EMAIL, ADMIN_PASSWORD
from app.core.security import hash_password
from app.database.database import Base, SessionLocal, engine
from app.models.admin import Admin  # noqa: F401 — registra o model no metadata
from app.models.event import Event  # noqa: F401 — registra o model no metadata
from app.models.events.models import Favorite  # noqa: F401 — registra o model no metadata
from app.repositories import admin_repository


def _seed_admin() -> None:
    """Cria o administrador inicial se não houver nenhum cadastrado."""
    db = SessionLocal()
    try:
        existing = admin_repository.get_by_email(db, ADMIN_EMAIL)
        if existing is None:
            hashed = hash_password(ADMIN_PASSWORD)
            admin_repository.create(db, ADMIN_EMAIL, hashed)
            print(f"✅ Admin seed criado: {ADMIN_EMAIL}")
        else:
            print(f"ℹ️  Admin já existe: {ADMIN_EMAIL}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifecycle hook: cria tabelas e seed antes de aceitar requisições."""
    Base.metadata.create_all(bind=engine)
    _seed_admin()
    yield


app = FastAPI(
    title="CIn Event Hub API",
    description="Hub centralizador de eventos acadêmicos do CIn/UFPE",
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS ────────────────────────────────────────────────────────────
# Permite o frontend React (Vite dev server) acessar a API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir para a URL do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(events_router)


@app.get("/", tags=["health"])
def health_check():
    """Health check — confirma que a API está no ar."""
    return {"status": "ok", "project": "cin-event-hub"}
