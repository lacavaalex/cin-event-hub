"""Roteiro de testes — lacunas das entregas de Wallyson Rodrigues.

Complementa (sem duplicar) ``test_auth_usuario.py``, ``test_cleanup_service.py`` e
``tests/api/test_rotas_integracao.py``:

- CT-02  .gitignore protege segredos
- CT-03..05  seed do admin (``app.main._seed_admin``)
- CT-10  senha vazia no login → 422
- CT-11  JWT expirado / assinado com outra chave → 401
- CT-12  admin rebaixado (is_admin = FALSE) perde acesso → 403
- CT-15..18  POST /events: data de hoje (Recife), espaços/campos ausentes, admin_id SET NULL
- CT-24..27  limpeza com favorito, rota /events/cleanup, CRON diário, resiliência do job
"""

import datetime as dt
import pathlib
import shutil
import subprocess

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import select, text

import app.main as main_module
from app.core.config import ADMIN_EMAIL, JWT_ALGORITHM, SECRET_KEY
from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.main import app
from app.models.event import Event
from app.models.events.models import Favorite
from app.models.user import User
from app.repositories import user_repository
from app.services.events import cleanup_scheduler
from app.services.events.cleanup_service import LOCAL_TZ, clean_expired_events

REPO = pathlib.Path(__file__).resolve().parents[2]
SENHA = "senha-forte-123"


def _usuario(db, email="admin@cin.ufpe.br", is_admin=True):
    return user_repository.create(
        db,
        name="Admin" if is_admin else "Aluno",
        email=email,
        hashed_password=hash_password(SENHA),
        profile_name="admin" if is_admin else "aluno",
        is_admin=is_admin,
    )


def _auth(email):
    return {"Authorization": f"Bearer {create_access_token({'sub': email})}"}


def _payload(**extra):
    dados = {
        "title": "Workshop de SQL",
        "description": "Introdução",
        "date": (dt.datetime.now(LOCAL_TZ).date() + dt.timedelta(days=30)).isoformat(),
        "time": "14:00:00",
        "location": "CIn",
        "event_type": "Workshop",
        "registration_link": "https://exemplo.com/inscricao",
    }
    dados.update(extra)
    return dados


def _evento(db, date, title="Evento"):
    evento = Event(
        title=title, description="Desc", date=date, time=dt.time(10, 0), location="CIn",
        event_type="Palestra", registration_link="https://exemplo.com", origin="manual",
    )
    db.add(evento)
    db.commit()
    return evento


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


# ---------- CT-02: .gitignore ----------

@pytest.mark.skipif(shutil.which("git") is None, reason="git não disponível")
@pytest.mark.parametrize("caminho,ignorado", [
    ("backend/.env", True),
    ("backend/gmail_token.json", True),
    ("credentials.json", True),
    ("gemini_key.json", True),
    ("backend/chave.pem", True),
    ("backend/.env.example", False),
])
def test_gitignore_protege_segredos(caminho, ignorado):
    r = subprocess.run(["git", "check-ignore", "-q", "--no-index", caminho], cwd=REPO)
    assert (r.returncode == 0) is ignorado


# ---------- CT-03..05: seed do admin ----------

@pytest.fixture()
def seed(db_session, monkeypatch):
    monkeypatch.setattr(main_module, "SessionLocal", lambda: db_session)
    return main_module._seed_admin


def test_seed_cria_admin_na_tabela_usuario(db_session, seed):
    seed()
    admin = user_repository.get_by_email(db_session, ADMIN_EMAIL)
    assert admin is not None and admin.is_admin is True
    assert admin.hashed_password != main_module.ADMIN_PASSWORD
    assert verify_password(main_module.ADMIN_PASSWORD, admin.hashed_password)


def test_seed_e_idempotente(db_session, seed):
    seed()
    seed()
    assert db_session.scalar(text("SELECT count(*) FROM usuario WHERE email = :e"), {"e": ADMIN_EMAIL}) == 1


def test_seed_nao_promove_usuario_comum(db_session, seed):
    _usuario(db_session, email=ADMIN_EMAIL, is_admin=False)
    seed()
    db_session.expire_all()
    usuario = user_repository.get_by_email(db_session, ADMIN_EMAIL)
    assert usuario.is_admin is False


# ---------- CT-10..12: login e JWT ----------

def test_login_senha_vazia_422(client, db_session):
    _usuario(db_session)
    assert client.post("/auth/login", json={"email": "admin@cin.ufpe.br", "password": ""}).status_code == 422


@pytest.mark.parametrize("chave,exp_delta", [
    (SECRET_KEY, dt.timedelta(minutes=-5)),       # expirado
    ("outra-chave-qualquer", dt.timedelta(minutes=5)),  # assinatura inválida
])
def test_jwt_expirado_ou_com_outra_chave_401(client, db_session, chave, exp_delta):
    _usuario(db_session)
    token = jwt.encode(
        {"sub": "admin@cin.ufpe.br", "exp": dt.datetime.now(dt.timezone.utc) + exp_delta},
        chave, algorithm=JWT_ALGORITHM,
    )
    r = client.post("/events", json=_payload(), headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_admin_rebaixado_perde_acesso_403(client, db_session):
    admin = _usuario(db_session)
    headers = _auth(admin.email)
    assert client.get("/events/admin", headers=headers).status_code == 200
    admin.is_admin = False
    db_session.commit()
    assert client.get("/events/admin", headers=headers).status_code == 403


# ---------- CT-15..18: POST /events ----------

def test_criar_evento_na_data_de_hoje_recife(client, db_session):
    _usuario(db_session)
    hoje = dt.datetime.now(LOCAL_TZ).date().isoformat()
    r = client.post("/events", json=_payload(date=hoje), headers=_auth("admin@cin.ufpe.br"))
    assert r.status_code == 201
    assert r.json()["date"] == hoje


@pytest.mark.parametrize("campo,valor", [
    ("title", "   "), ("description", "   "), ("location", "   "), ("title", None),
])
def test_criar_evento_com_espacos_ou_campo_ausente_422(client, db_session, campo, valor):
    _usuario(db_session)
    payload = _payload()
    if valor is None:
        payload.pop(campo)
    else:
        payload[campo] = valor
    assert client.post("/events", json=payload, headers=_auth("admin@cin.ufpe.br")).status_code == 422
    assert db_session.scalar(text("SELECT count(*) FROM events")) == 0


def test_excluir_admin_criador_mantem_evento_com_admin_id_nulo(client, db_session):
    admin = _usuario(db_session)
    r = client.post("/events", json=_payload(), headers=_auth(admin.email))
    evento_id = r.json()["id"]
    db_session.delete(admin)
    db_session.commit()
    linha = db_session.execute(
        text("SELECT admin_id FROM events WHERE id_event = :i"), {"i": evento_id}
    ).one()
    assert linha.admin_id is None


# ---------- CT-24..27: limpeza ----------

def test_limpeza_remove_favorito_do_evento_e_mantem_usuario(db_session):
    usuario = _usuario(db_session, email="aluno@cin.ufpe.br", is_admin=False)
    evento = _evento(db_session, dt.date(2026, 8, 1))
    db_session.add(Favorite(user_id=usuario.id, event_id=evento.id))
    db_session.commit()

    report = clean_expired_events(db_session, reference_date=dt.date(2026, 8, 2))

    assert report.expired_count == 1
    assert db_session.scalar(select(Favorite)) is None
    assert db_session.get(User, usuario.id) is not None


def test_cleanup_negado_para_usuario_comum_403(client, db_session):
    _usuario(db_session, email="aluno@cin.ufpe.br", is_admin=False)
    r = client.post("/events/cleanup", headers=_auth("aluno@cin.ufpe.br"))
    assert r.status_code == 403


def test_cleanup_sem_reference_date_usa_hoje(client, db_session):
    _usuario(db_session)
    hoje = dt.datetime.now(LOCAL_TZ).date()
    _evento(db_session, hoje - dt.timedelta(days=1), title="Ontem")
    _evento(db_session, hoje, title="Hoje")

    r = client.post("/events/cleanup", headers=_auth("admin@cin.ufpe.br"))

    assert r.status_code == 200
    corpo = r.json()
    assert corpo["reference_date"] == hoje.isoformat()
    assert corpo["deleted_titles"] == ["Ontem"]
    assert db_session.scalar(text("SELECT count(*) FROM events")) == 1


def test_scheduler_em_modo_cron_diario(monkeypatch):
    from apscheduler.triggers.cron import CronTrigger

    monkeypatch.setattr(cleanup_scheduler, "CLEANUP_ENABLED", True)
    monkeypatch.setattr(cleanup_scheduler, "CLEANUP_INTERVAL_MINUTES", None)
    monkeypatch.setattr(cleanup_scheduler, "CLEANUP_CRON_HOUR", 3)
    monkeypatch.setattr(cleanup_scheduler, "CLEANUP_CRON_MINUTE", 0)
    cleanup_scheduler.start_cleanup_scheduler()
    try:
        [job] = cleanup_scheduler._scheduler.get_jobs()
        assert job.id == "limpeza_eventos_expirados"
        assert isinstance(job.trigger, CronTrigger)
        campos = {f.name: str(f) for f in job.trigger.fields}
        assert (campos["hour"], campos["minute"]) == ("3", "0")
        assert str(job.trigger.timezone) == "America/Recife"
    finally:
        cleanup_scheduler.shutdown_cleanup_scheduler()
    assert cleanup_scheduler._scheduler is None


def test_job_de_limpeza_nao_quebra_com_excecao(db_session, monkeypatch):
    monkeypatch.setattr(cleanup_scheduler, "SessionLocal", lambda: db_session)

    def _falha(_db):
        raise RuntimeError("banco fora do ar")

    monkeypatch.setattr(cleanup_scheduler, "clean_expired_events", _falha)
    assert cleanup_scheduler.run_cleanup_job() is None
