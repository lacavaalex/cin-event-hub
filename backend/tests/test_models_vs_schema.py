"""Conexão backend ↔ banco: os models ORM batem com as tabelas do schema SQL?

O schema oficial (``database/001_schema.sql``) é aplicado no banco de testes pelo
``conftest.py``. Aqui comparamos o que o SQLAlchemy espera com o que o PostgreSQL
realmente tem. Se alguém renomear uma coluna num lado e esquecer do outro, estes
testes falham antes da aplicação quebrar em produção.

``Admin`` fica de fora de propósito: a tabela ``admins`` não faz parte do schema SQL
ainda (é criada pelo ``create_all``) e será tratada junto com o Event/Admin.
"""

import pytest
from sqlalchemy import String, inspect, text

from app.models.event import Event
from app.models.events.models import Favorite
from app.models.extraction_log import ExtractionLog
from app.models.user import User

MODELS = [User, Event, ExtractionLog, Favorite]
TABELAS = {"usuario", "events", "extracao", "favorito"}


def test_conecta_no_banco(engine):
    with engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_tabelas_do_schema_existem(engine):
    assert TABELAS <= set(inspect(engine).get_table_names())


def test_cada_model_aponta_para_uma_tabela_do_schema():
    assert {m.__tablename__ for m in MODELS} == TABELAS


@pytest.mark.parametrize("model", MODELS, ids=lambda m: m.__tablename__)
def test_colunas_do_model_existem_no_banco(engine, model):
    reais = {c["name"]: c for c in inspect(engine).get_columns(model.__tablename__)}
    for coluna in model.__table__.columns:
        assert coluna.name in reais, f"{model.__tablename__}.{coluna.name} não existe no banco"
        real = reais[coluna.name]
        # tipo Python compatível (int, str, date, ...)
        try:
            esperado = coluna.type.python_type
        except NotImplementedError:
            continue
        try:
            obtido = real["type"].python_type
        except NotImplementedError:
            continue
        assert esperado == obtido or issubclass(obtido, esperado) or issubclass(esperado, obtido), (
            f"{model.__tablename__}.{coluna.name}: model {esperado}, banco {obtido}"
        )
        if isinstance(coluna.type, String) and coluna.type.length is not None:
            assert real["type"].length == coluna.type.length, (
                f"{model.__tablename__}.{coluna.name}: tamanho diferente do banco"
            )
        # NOT NULL do banco não pode ser mais frouxo no model, nem o contrário
        if not coluna.primary_key:
            assert coluna.nullable == real["nullable"], (
                f"{model.__tablename__}.{coluna.name}: nullable difere do banco"
            )


@pytest.mark.parametrize("model", MODELS, ids=lambda m: m.__tablename__)
def test_colunas_do_banco_sem_model_nao_travam_insert(engine, model):
    """Coluna que o model desconhece precisa ser opcional ou ter default,
    senão todo INSERT feito pelo ORM falharia."""
    mapeadas = {c.name for c in model.__table__.columns}
    for real in inspect(engine).get_columns(model.__tablename__):
        if real["name"] in mapeadas:
            continue
        livre = real["nullable"] or real["default"] is not None or real.get("identity")
        assert livre, f"{model.__tablename__}.{real['name']} é obrigatória e o model não a mapeia"


@pytest.mark.parametrize("model", MODELS, ids=lambda m: m.__tablename__)
def test_chave_primaria_do_model_igual_a_do_banco(engine, model):
    banco = inspect(engine).get_pk_constraint(model.__tablename__)["constrained_columns"]
    assert {c.name for c in model.__table__.primary_key.columns} == set(banco)


def test_chaves_estrangeiras_do_model_existem_no_banco(engine):
    insp = inspect(engine)
    for model in MODELS:
        reais = {
            (tuple(fk["constrained_columns"]), fk["referred_table"], tuple(fk["referred_columns"]))
            for fk in insp.get_foreign_keys(model.__tablename__)
        }
        for fk in model.__table__.foreign_key_constraints:
            chave = (
                tuple(c.name for c in fk.columns),
                fk.referred_table.name,
                tuple(e.column.name for e in fk.elements),
            )
            assert chave in reais, f"FK {chave} de {model.__tablename__} não existe no banco"
