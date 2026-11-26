"""Ponto de entrada da aplicação FastAPI — CIn Event Hub Backend.

Ao iniciar:
1. Cria no PostgreSQL as tabelas que ainda não existirem (as de database/001_schema.sql já vêm prontas).
2. Gera o admin seed (usuario com is_admin = TRUE) se ainda não existir (credenciais no .env).
3. Registra os routers de autenticação e eventos.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth.router import router as auth_router
from app.api.eventos.router import router as events_router
from app.api.extracao.router import router as extraction_router
from app.core.config import ADMIN_EMAIL, ADMIN_NAME, ADMIN_PASSWORD, ADMIN_PROFILE_NAME
from app.core.security import hash_password
from app.database.database import Base, SessionLocal, engine
from app.models.event import Event  # noqa: F401 — registra o model no metadata
from app.models.user import User  # noqa: F401 — registra o model no metadata (usuario/admin, FK de favorito e events)
from app.models.extraction_log import ExtractionLog  # noqa: F401 — registra o model no metadata
from app.models.events.models import Favorite  # noqa: F401 — registra o model no metadata
from app.repositories import user_repository
from app.services.events.cleanup_scheduler import (
    shutdown_cleanup_scheduler,
    start_cleanup_scheduler,
)
from app.services.extracao_email.scheduler import shutdown_scheduler, start_scheduler


def _seed_admin() -> None:
    """Cria o administrador inicial na tabela ``usuario`` (is_admin = TRUE).

    Modelo EER: administrador não é uma entidade própria, é um USUARIO com a
    flag ``is_admin``. Se já existir um usuário com o e-mail configurado, nada é
    alterado (um usuário comum não é promovido automaticamente).
    """
    # Nao cria administradores usando credenciais padrao de demonstracao.
    # Uma conta ja existente permanece no banco e pode fazer login normalmente.
    if not ADMIN_EMAIL and not ADMIN_PASSWORD:
        return
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        raise RuntimeError("Configure ADMIN_EMAIL e ADMIN_PASSWORD juntos para criar o admin inicial")

    db = SessionLocal()
    try:
        existing = user_repository.get_by_email(db, ADMIN_EMAIL)
        if existing is None:
            user_repository.create(
                db,
                name=ADMIN_NAME,
                email=ADMIN_EMAIL,
                hashed_password=hash_password(ADMIN_PASSWORD),
                profile_name=ADMIN_PROFILE_NAME,
                is_admin=True,
            )
            print(f"✅ Admin seed criado: {ADMIN_EMAIL}")
        elif existing.is_admin:
            print(f"ℹ️  Admin já existe: {ADMIN_EMAIL}")
        else:
            print(
                f"⚠️  {ADMIN_EMAIL} já existe como usuário comum (is_admin = FALSE); "
                "não foi promovido a administrador."
            )
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifecycle hook: cria tabelas e seed antes de aceitar requisições."""
    # checkfirst (padrão): não recria nem altera usuario/events/extracao/favorito,
    # que nascem do database/001_schema.sql com todas as restrições do banco.
    Base.metadata.create_all(bind=engine)
    _seed_admin()
    start_scheduler()
    start_cleanup_scheduler()
    yield
    shutdown_cleanup_scheduler()
    shutdown_scheduler()



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
app.include_router(extraction_router)


@app.get("/", tags=["health"])
def health_check():
    """Health check — confirma que a API está no ar."""
    return {"status": "ok", "project": "cin-event-hub"}
