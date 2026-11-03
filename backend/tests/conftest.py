"""Fixtures compartilhadas dos testes do backend — rodam em PostgreSQL.

Por que PostgreSQL (e não SQLite)
---------------------------------
O backend começou com SQLite em memória nos testes (padrão de desenvolvimento
enquanto o PostgreSQL não estava pronto). O banco de produção é PostgreSQL e as
regras de negócio (CHECKs, FKs, tipos) vivem no ``database/001_schema.sql``;
testar em SQLite não exercitava essas regras. Veja ``docs/migracao-postgresql.md``.

Como funciona
-------------
1. Uma vez por execução do pytest, cria o banco temporário ``iesi_test_backend``
   (apaga se sobrou de uma execução anterior).
2. Aplica ``database/001_schema.sql`` — as tabelas que o schema define
   (users, extractions, events) nascem com todas as restrições do banco.
3. ``Base.metadata.create_all`` cria só o que o schema ainda não tem
   (admins, extraction_logs, favorites). Tabelas que já existem são mantidas.
4. Cada teste começa com as tabelas vazias (TRUNCATE ... RESTART IDENTITY).
5. No fim, apaga o banco temporário. Nenhum outro banco do servidor é tocado.

Servidor: por padrão ``postgresql://postgres:dev@localhost:5432/postgres``
(o mesmo de ``python database/run_tests.py``). Para outro servidor, defina
``DATABASE_ADMIN_URL``.
"""

import os
import pathlib

import psycopg
import pytest
from psycopg import sql
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.database import Base
# Os models são importados para serem registrados no Base.metadata.
from app.models.admin import Admin  # noqa: F401
from app.models.event import Event  # noqa: F401
from app.models.events.models import Favorite  # noqa: F401
from app.models.extraction_log import ExtractionLog  # noqa: F401
from app.models.user import User  # noqa: F401

ADMIN_URL = os.environ.get(
    "DATABASE_ADMIN_URL", "postgresql://postgres:dev@localhost:5432/postgres"
)
TEST_DB = "iesi_test_backend"
SCHEMA_SQL = pathlib.Path(__file__).resolve().parents[2] / "database" / "001_schema.sql"


def _url_do_banco(database: str) -> str:
    """URL do SQLAlchemy (driver psycopg 3) para um banco do servidor de testes."""
    return (
        make_url(ADMIN_URL)
        .set(drivername="postgresql+psycopg", database=database)
        .render_as_string(hide_password=False)
    )


@pytest.fixture(scope="session")
def engine():
    """Banco temporário com o schema oficial (database/001_schema.sql) aplicado."""
    try:
        admin = psycopg.connect(ADMIN_URL, autocommit=True)
    except psycopg.OperationalError as exc:
        pytest.exit(
            "PostgreSQL inacessível para os testes do backend "
            f"({exc}). Suba um servidor e/ou defina DATABASE_ADMIN_URL "
            "(veja docs/migracao-postgresql.md).",
            returncode=2,
        )
    banco = sql.Identifier(TEST_DB)
    admin.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(banco))
    admin.execute(sql.SQL("CREATE DATABASE {}").format(banco))

    # 1) schema oficial: tabelas e restrições do banco
    teste = make_url(ADMIN_URL).set(database=TEST_DB).render_as_string(hide_password=False)
    with psycopg.connect(teste, autocommit=True) as conn:
        conn.execute(SCHEMA_SQL.read_text(encoding="utf-8"))

    # 2) o que o schema ainda não cobre (admins, extraction_logs, favorites)
    eng = create_engine(_url_do_banco(TEST_DB), pool_pre_ping=True)
    Base.metadata.create_all(bind=eng)
    try:
        yield eng
    finally:
        eng.dispose()
        admin.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(banco))
        admin.close()


@pytest.fixture()
def db_session(engine):
    """Sessão em um banco limpo: todas as tabelas esvaziadas antes de cada teste."""
    # todas as tabelas do banco (inclui as do schema SQL que não têm model, como
    # extracao e email_associado)
    tabelas = ", ".join(f'"{nome}"' for nome in inspect(engine).get_table_names())
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {tabelas} RESTART IDENTITY CASCADE"))
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = factory()
    try:
        yield session
    finally:
        session.close()
