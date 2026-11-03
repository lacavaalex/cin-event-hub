"""Conexão com o banco de dados (SQLAlchemy 2.x).

Usa PostgreSQL (driver psycopg 3) em desenvolvimento, testes e produção.
A URL vem de DATABASE_URL (.env):
    postgresql+psycopg://usuario:senha@localhost:5432/eventos
O SQLite foi abandonado — veja docs/migracao-postgresql.md.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Classe base de todos os models ORM."""


def get_db() -> Iterator[Session]:
    """Dependência do FastAPI: uma sessão por requisição, sempre fechada no fim."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
