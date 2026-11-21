"""Configurações centrais da aplicação — carregadas a partir de variáveis de ambiente."""

import os

from dotenv import load_dotenv

load_dotenv()

# ── Banco de dados ──────────────────────────────────────────────────
# PostgreSQL é o banco do projeto (dev, testes e produção). O padrão abaixo é o
# PostgreSQL local descrito em docs/migracao-postgresql.md; para outro servidor,
# defina DATABASE_URL no .env. SQLite deixou de ser suportado.
DATABASE_URL: str = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://postgres:dev@localhost:5432/eventos"
)

# ── JWT ─────────────────────────────────────────────────────────────
SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "troque-esta-chave-em-producao"))
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# ── Admin seed ──────────────────────────────────────────────────────
# O administrador inicial é um registro da tabela ``usuario`` com is_admin = TRUE
# (modelo EER: não existe entidade/tabela própria de admin).
ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@cin.ufpe.br")
ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "123456")
ADMIN_NAME: str = os.getenv("ADMIN_NAME", "Administrador")
ADMIN_PROFILE_NAME: str = os.getenv("ADMIN_PROFILE_NAME", "admin")

# ── Extração de e-mails ────────────────────────────────────
EXTRACTION_ENABLED: bool = os.getenv("EXTRACTION_ENABLED", "true").lower() in {
    "1", "true", "yes", "on"
}
EXTRACTION_INTERVAL_MINUTES: int = int(
    os.getenv("EXTRACTION_INTERVAL_MINUTES", "720")
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

# ── Limpeza de eventos expirados (US 5.1 / 5.2) ──────────────
CLEANUP_ENABLED: bool = os.getenv("CLEANUP_ENABLED", "true").lower() in {
    "1", "true", "yes", "on"
}
CLEANUP_CRON_HOUR: int = int(os.getenv("CLEANUP_CRON_HOUR", "3"))
CLEANUP_CRON_MINUTE: int = int(os.getenv("CLEANUP_CRON_MINUTE", "0"))
_raw_cleanup_interval = os.getenv("CLEANUP_INTERVAL_MINUTES")
CLEANUP_INTERVAL_MINUTES: int | None = (
    int(_raw_cleanup_interval) if _raw_cleanup_interval else None
)

