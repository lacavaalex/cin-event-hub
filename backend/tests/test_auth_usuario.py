"""US 1.1 / 1.2 — autenticação pela entidade USUARIO do modelo EER.

Não existe mais tabela/model ``Admin``: o administrador é um registro de
``usuario`` com ``is_admin = TRUE``. Estes testes rodam no PostgreSQL de testes
(``conftest.py``) e cobrem repositório, serviço, rota de login e a dependência
que protege as rotas de administrador.
"""

import datetime as dt
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password
from app.database import get_db
from app.main import app
from app.models.event import Event
from app.repositories import user_repository
from app.services import auth_service

LOCAL_TZ = ZoneInfo("America/Recife")

SENHA = "senha-forte-123"


def _usuario(db, email="admin@cin.ufpe.br", is_admin=True, senha=SENHA):
    return user_repository.create(
        db,
        name="Admin" if is_admin else "Aluno",
        email=email,
        hashed_password=hash_password(senha),
        profile_name="admin" if is_admin else "aluno",
        is_admin=is_admin,
    )


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def _evento_payload():
    return {
        "title": "Palestra de IA",
        "description": "Descrição",
        "date": (dt.datetime.now(LOCAL_TZ).date() + dt.timedelta(days=30)).isoformat(),
        "time": "10:00:00",
        "location": "CIn",
        "event_type": "Palestra",
        "registration_link": "https://exemplo.com",
    }


# ---------- modelo ----------

def test_model_admin_nao_existe_mais():
    with pytest.raises(ModuleNotFoundError):
        __import__("app.models.admin")


# ---------- repositório ----------

def test_repositorio_cria_admin_na_tabela_usuario(db_session):
    admin = _usuario(db_session)
    db_session.refresh(admin)
    assert admin.id >= 1
    assert admin.is_admin is True
    assert admin.created_at == dt.datetime.now(LOCAL_TZ).date()


def test_get_admin_by_email_ignora_usuario_comum(db_session):
    _usuario(db_session, email="aluno@cin.ufpe.br", is_admin=False)
    assert user_repository.get_by_email(db_session, "aluno@cin.ufpe.br") is not None
    assert user_repository.get_admin_by_email(db_session, "aluno@cin.ufpe.br") is None


# ---------- serviço ----------

def test_login_de_admin_retorna_token(db_session):
    _usuario(db_session)
    assert auth_service.authenticate_admin(db_session, "admin@cin.ufpe.br", SENHA)


@pytest.mark.parametrize("email, senha", [
    ("admin@cin.ufpe.br", "errada"),
    ("ninguem@cin.ufpe.br", SENHA),
])
def test_login_com_credenciais_invalidas(db_session, email, senha):
    _usuario(db_session)
    with pytest.raises(auth_service.InvalidCredentialsError):
        auth_service.authenticate_admin(db_session, email, senha)


def test_login_de_usuario_comum_e_recusado(db_session):
    _usuario(db_session, email="aluno@cin.ufpe.br", is_admin=False)
    with pytest.raises(auth_service.NotAdminError):
        auth_service.authenticate_admin(db_session, "aluno@cin.ufpe.br", SENHA)


# ---------- rota POST /auth/login ----------

def test_rota_login_admin_200(client, db_session):
    _usuario(db_session)
    resposta = client.post("/auth/login", json={"email": "admin@cin.ufpe.br", "password": SENHA})
    assert resposta.status_code == 200
    assert resposta.json()["token"]


def test_rota_login_senha_errada_401(client, db_session):
    _usuario(db_session)
    resposta = client.post("/auth/login", json={"email": "admin@cin.ufpe.br", "password": "x"})
    assert resposta.status_code == 401


def test_rota_login_usuario_comum_403(client, db_session):
    _usuario(db_session, email="aluno@cin.ufpe.br", is_admin=False)
    resposta = client.post("/auth/login", json={"email": "aluno@cin.ufpe.br", "password": SENHA})
    assert resposta.status_code == 403


# ---------- rotas protegidas (get_current_admin) ----------

def _auth(email):
    return {"Authorization": f"Bearer {create_access_token({'sub': email})}"}


def test_admin_cria_evento_e_fica_registrado_como_quem_cadastrou(client, db_session):
    admin = _usuario(db_session)
    resposta = client.post("/events", json=_evento_payload(), headers=_auth(admin.email))
    assert resposta.status_code == 201
    evento = db_session.get(Event, resposta.json()["id"])
    assert evento.admin_id == admin.id


def test_usuario_comum_nao_acessa_rota_de_admin(client, db_session):
    _usuario(db_session, email="aluno@cin.ufpe.br", is_admin=False)
    resposta = client.post("/events", json=_evento_payload(), headers=_auth("aluno@cin.ufpe.br"))
    assert resposta.status_code == 403


def test_token_de_usuario_removido_perde_acesso(client, db_session):
    admin = _usuario(db_session)
    headers = _auth(admin.email)
    db_session.delete(admin)
    db_session.commit()
    assert client.post("/events", json=_evento_payload(), headers=headers).status_code == 403


def test_token_invalido_401(client):
    resposta = client.post(
        "/events", json=_evento_payload(), headers={"Authorization": "Bearer invalido"}
    )
    assert resposta.status_code == 401
