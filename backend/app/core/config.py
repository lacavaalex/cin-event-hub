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

# ── Extração de e-mails ────────────────────────────────────
EXTRACTION_ENABLED: bool = os.getenv("EXTRACTION_ENABLED", "true").lower() in {
    "1", "true", "yes", "on"
}
EXTRACTION_INTERVAL_MINUTES: int = int(
    os.getenv("EXTRACTION_INTERVAL_MINUTES", "15")
)
GMAIL_CREDENTIALS_FILE: str = os.getenv(
    "GMAIL_CREDENTIALS_FILE", "./gmail_credentials.json"
)
GMAIL_TOKEN_FILE: str = os.getenv("GMAIL_TOKEN_FILE", "./gmail_token.json")
GMAIL_QUERY: str = os.getenv("GMAIL_QUERY", "newer_than:7d")
GMAIL_MAX_RESULTS: int = int(os.getenv("GMAIL_MAX_RESULTS", "50"))

# Chave do Gemini
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
GEMINI_MAX_OUTPUT_TOKENS: int = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "1024"))
