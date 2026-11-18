"""Gravação e leitura pelos models ORM, com as restrições reais do PostgreSQL.

Complementa os testes SQL de ``database/tests``: aqui o caminho é o do backend
(SQLAlchemy → PostgreSQL), para provar que os models respeitam as regras do banco.
"""

import datetime as dt

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from app.models.event import Event
from app.models.events.models import Favorite
from app.models.extraction_log import ExtractionLog
from app.models.user import User


def _usuario(db, email="ana@cin.ufpe.br", **extra):
    dados = dict(name="Ana", email=email, hashed_password="hash", profile_name="ana")
    dados.update(extra)
    usuario = User(**dados)
    db.add(usuario)
    db.commit()
    return usuario


def _evento(db, **extra):
    dados = dict(
        title="Palestra", description="Desc", date=dt.date(2030, 1, 1), time=dt.time(10, 0),
        location="CIn", event_type="Palestra", registration_link="https://exemplo.com",
    )
    dados.update(extra)
    evento = Event(**dados)
    db.add(evento)
    db.commit()
    return evento


def _log(db, msg="msg-1", status="erro", **extra):
    log = ExtractionLog(gmail_message_id=msg, source_email="a@b.com", status=status, **extra)
    db.add(log)
    db.commit()
    return log


# ---------- usuario ----------

def test_usuario_defaults_do_banco(db_session):
    usuario = _usuario(db_session)
    db_session.refresh(usuario)
    assert usuario.id >= 1
    assert usuario.is_admin is False
    assert usuario.created_at == dt.date.today()


def test_usuario_email_duplicado_e_recusado(db_session):
    _usuario(db_session)
    with pytest.raises(IntegrityError):
        _usuario(db_session)
    db_session.rollback()


@pytest.mark.parametrize("campo", ["name", "email", "hashed_password", "profile_name"])
def test_usuario_campo_vazio_e_recusado(db_session, campo):
    with pytest.raises(IntegrityError):
        _usuario(db_session, **{campo: "  "})
    db_session.rollback()


def test_apagar_usuario_remove_favoritos_e_mantem_evento(db_session):
    usuario, evento = _usuario(db_session), _evento(db_session)
    db_session.add(Favorite(user_id=usuario.id, event_id=evento.id))
    db_session.commit()
    db_session.delete(usuario)
    db_session.commit()
    assert db_session.scalar(select(Favorite)) is None
    assert db_session.get(Event, evento.id) is not None


# ---------- favorito ----------

def test_favorito_grava_e_le(db_session):
    usuario, evento = _usuario(db_session), _evento(db_session)
    db_session.add(Favorite(user_id=usuario.id, event_id=evento.id))
    db_session.commit()
    fav = db_session.scalar(select(Favorite))
    assert (fav.user_id, fav.event_id) == (usuario.id, evento.id)


def test_favorito_duplicado_e_recusado(db_session):
    usuario, evento = _usuario(db_session), _evento(db_session)
    db_session.add(Favorite(user_id=usuario.id, event_id=evento.id))
    db_session.commit()
    db_session.add(Favorite(user_id=usuario.id, event_id=evento.id))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_favorito_com_usuario_ou_evento_inexistente_e_recusado(db_session):
    usuario, evento = _usuario(db_session), _evento(db_session)
    for par in [(usuario.id, 9999), (9999, evento.id)]:
        db_session.add(Favorite(user_id=par[0], event_id=par[1]))
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()


def test_apagar_evento_remove_favoritos(db_session):
    usuario, evento = _usuario(db_session), _evento(db_session)
    db_session.add(Favorite(user_id=usuario.id, event_id=evento.id))
    db_session.commit()
    db_session.delete(evento)
    db_session.commit()
    assert db_session.scalar(select(Favorite)) is None
    assert db_session.get(User, usuario.id) is not None


# ---------- events ----------

def test_evento_defaults_do_banco(db_session):
    evento = _evento(db_session)
    db_session.refresh(evento)
    assert (evento.status, evento.origin) == ("active", "manual")
    assert evento.created_at is not None and evento.updated_at is not None


@pytest.mark.parametrize("extra", [
    {"event_type": "Show"},
    {"status": "pendente"},
    {"title": " "},
    {"registration_link": ""},            # vazio só vale fora da origem manual
    {"registration_link": "ftp://x.com"},
])
def test_evento_invalido_e_recusado(db_session, extra):
    with pytest.raises(IntegrityError):
        _evento(db_session, **extra)
    db_session.rollback()


def test_evento_de_email_aceita_link_vazio(db_session):
    evento = _evento(db_session, origin="email", registration_link="")
    assert evento.id is not None


# ---------- extracao ----------

def test_extracao_defaults_e_json_ida_e_volta(db_session):
    dados = {"title": "Seminário", "tags": ["ia", "bd"], "vagas": 30}
    log = _log(db_session, status="processado_ia", extracted_data=dados)
    db_session.expire_all()
    lido = db_session.get(ExtractionLog, log.id)
    assert lido.extracted_data == dados
    assert lido.created_at is not None
    assert lido.event_id is None


@pytest.mark.parametrize("status", [
    "processado", "processado_ia", "ignorado", "nao_processado", "extracao_incompleta", "erro",
])
def test_extracao_aceita_os_seis_status(db_session, status):
    assert _log(db_session, msg=f"m-{status}", status=status).id is not None


def test_extracao_status_invalido_e_recusado(db_session):
    with pytest.raises(IntegrityError):
        _log(db_session, status="success")
    db_session.rollback()


def test_extracao_message_id_duplicado_ou_vazio_e_recusado(db_session):
    _log(db_session, msg="dup")
    for msg in ("dup", " "):
        with pytest.raises(IntegrityError):
            _log(db_session, msg=msg)
        db_session.rollback()


def test_extracao_event_id_so_com_status_processado(db_session):
    evento = _evento(db_session, origin="email")
    with pytest.raises(IntegrityError):
        _log(db_session, msg="x", status="erro", event_id=evento.id)
    db_session.rollback()
    assert _log(db_session, msg="y", status="processado", event_id=evento.id).event_id == evento.id


def test_extracao_event_id_inexistente_e_recusado(db_session):
    with pytest.raises(IntegrityError):
        _log(db_session, status="processado", event_id=9999)
    db_session.rollback()


def test_apagar_evento_mantem_log_com_event_id_nulo(db_session):
    evento = _evento(db_session, origin="email")
    log = _log(db_session, status="processado", event_id=evento.id)
    db_session.delete(evento)
    db_session.commit()
    db_session.expire_all()
    assert db_session.get(ExtractionLog, log.id).event_id is None


def test_apagar_log_mantem_evento(db_session):
    evento = _evento(db_session, origin="email")
    log = _log(db_session, status="processado", event_id=evento.id)
    db_session.delete(log)
    db_session.commit()
    assert db_session.get(Event, evento.id) is not None


def test_truncate_entre_testes_zera_as_tabelas(db_session):
    for tabela in ("usuario", "events", "extracao", "favorito"):
        assert db_session.execute(text(f"SELECT count(*) FROM {tabela}")).scalar() == 0
