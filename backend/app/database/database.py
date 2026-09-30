"""Conexão com o PostgreSQL (SQLAlchemy 2.x + driver psycopg 3)."""
import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Ex.: postgresql+psycopg://usuario:senha@localhost:5432/eventos
DATABASE_URL = os.environ["DATABASE_URL"]

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
