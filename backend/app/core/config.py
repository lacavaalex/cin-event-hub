"""Configurações centrais da aplicação — carregadas a partir de variáveis de ambiente."""

import os

from dotenv import load_dotenv

load_dotenv()

# ── Banco de dados ──────────────────────────────────────────────────
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./eventos.db")

# ── JWT ─────────────────────────────────────────────────────────────
SECRET_KEY: str = os.getenv("SECRET_KEY", "troque-esta-chave-em-producao")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# ── Admin seed ──────────────────────────────────────────────────────
ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@cin.ufpe.br")
ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "123456")
