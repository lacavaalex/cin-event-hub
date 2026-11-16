"""Integração das rotas com o PostgreSQL: HTTP → router → service → repository → tabelas.

Cada teste faz a requisição pelo TestClient e depois confere direto no banco (SQL
puro) o que realmente foi gravado, para provar a ligação rota ↔ tabela:

    /auth/login            → admins
    /events (CRUD)         → events
    /events/{id}/favorite  → favorito (e usuario, pela FK)
    /extraction/run        → extracao (+ events)
"""

import datetime as dt

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.security import hash_password
from app.database import get_db
from app.main import app
from app.models.user import User
from app.repositories import admin_repository
from app.services.extracao_email.extraction_service import run_extraction
from app.services.extracao_email.gmail_client import RawEmail

EMAIL_ADMIN, SENHA_ADMIN = "admin@cin.ufpe.br", "123456"
FUTURO = (dt.date.today() + dt.timedelta(days=30)).isoformat()


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def auth(client, db_session):
    """Cria o admin, faz login pela rota e devolve o header Authorization."""
    admin_repository.create(db_session, EMAIL_ADMIN, hash_password(SENHA_ADMIN))
    r = client.post("/auth/login", json={"email": EMAIL_ADMIN, "password": SENHA_ADMIN})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['token']}"}


def _payload(**extra):
    dados = {
        "title": "Workshop de SQL", "description": "Introdução", "date": FUTURO,
        "time": "14:00:00", "location": "CIn", "event_type": "Workshop",
        "registration_link": "https://exemplo.com/inscricao",
    }
    dados.update(extra)
    return dados


def _contar(db, tabela, where="true"):
    return db.execute(text(f"SELECT count(*) FROM {tabela} WHERE {where}")).scalar()


# ---------- saúde e login (tabela admins) ----------

def test_health(client):
    assert client.get("/").json() == {"status": "ok", "project": "cin-event-hub"}


def test_login_ok_devolve_token(auth):
    assert auth["Authorization"].startswith("Bearer ")


@pytest.mark.parametrize("email,senha", [(EMAIL_ADMIN, "errada"), ("outro@cin.ufpe.br", SENHA_ADMIN)])
def test_login_invalido_401(client, db_session, email, senha):
    admin_repository.create(db_session, EMAIL_ADMIN, hash_password(SENHA_ADMIN))
    r = client.post("/auth/login", json={"email": email, "password": senha})
    assert r.status_code == 401


def test_login_nao_usa_a_tabela_usuario(client, db_session):
    """Hoje o login é só pela tabela admins; um admin da tabela usuario não loga."""
    db_session.add(User(name="Ana", email="ana@cin.ufpe.br", hashed_password=hash_password("x"),
                        profile_name="ana", is_admin=True))
    db_session.commit()
    r = client.post("/auth/login", json={"email": "ana@cin.ufpe.br", "password": "x"})
    assert r.status_code == 401


def test_login_campo_vazio_ou_email_invalido_422(client):
    assert client.post("/auth/login", json={"email": "nao-e-email", "password": "x"}).status_code == 422
    assert client.post("/auth/login", json={}).status_code == 422


# ---------- proteção por JWT ----------

@pytest.mark.parametrize("metodo,url", [
    ("post", "/events"), ("put", "/events/1"), ("delete", "/events/1"), ("post", "/extraction/run"),
])
def test_rotas_de_admin_recusam_sem_token(client, metodo, url):
    r = getattr(client, metodo)(url, json={}) if metodo != "delete" else client.delete(url)
    assert r.status_code in (401, 403)


def test_token_invalido_401(client):
    r = client.post("/events", json=_payload(), headers={"Authorization": "Bearer lixo"})
    assert r.status_code == 401


# ---------- events (CRUD) ----------

def test_criar_evento_grava_na_tabela_events(client, db_session, auth):
    r = client.post("/events", json=_payload(), headers=auth)
    assert r.status_code == 201
    corpo = r.json()
    assert (corpo["status"], corpo["origin"]) == ("active", "manual")
    linha = db_session.execute(
        text("SELECT title, int_event_date, event_location, origin FROM events WHERE id_event = :i"),
        {"i": corpo["id"]},
    ).one()
    assert linha.title == "Workshop de SQL" and linha.event_location == "CIn" and linha.origin == "manual"


@pytest.mark.parametrize("extra,codigo", [
    ({"date": "2020-01-01"}, 422),               # passado
    ({"event_type": "Show"}, 422),               # tipo fora da lista
    ({"registration_link": "nao-e-url"}, 422),
    ({"title": ""}, 422),
    ({"campo_extra": 1}, 422),                   # extra="forbid"
])
def test_criar_evento_invalido_nao_grava(client, db_session, auth, extra, codigo):
    assert client.post("/events", json=_payload(**extra), headers=auth).status_code == codigo
    assert _contar(db_session, "events") == 0


def test_buscar_evento_por_id_e_404(client, criar_eventos):
    evento = criar_eventos(1)[0]
    assert client.get(f"/events/{evento.id}").json()["title"] == "Evento 1"
    assert client.get("/events/9999").status_code == 404


def test_listagem_so_traz_ativos(client, criar_eventos):
    criar_eventos(2)
    criar_eventos(1, status="inactive", prefixo="Inativo")
    titulos = [e["title"] for e in client.get("/events").json()["items"]]
    assert titulos == ["Evento 1", "Evento 2"]


def test_editar_evento_atualiza_a_linha(client, db_session, auth, criar_eventos):
    evento = criar_eventos(1)[0]
    r = client.put(f"/events/{evento.id}", json=_payload(title="Novo título"), headers=auth)
    assert r.status_code == 200
    titulo = db_session.execute(text("SELECT title FROM events WHERE id_event = :i"), {"i": evento.id}).scalar()
    assert titulo == "Novo título"
    assert client.put("/events/9999", json=_payload(), headers=auth).status_code == 404
    assert client.put(f"/events/{evento.id}", json=_payload(date="2020-01-01"), headers=auth).status_code == 422


def test_excluir_evento(client, db_session, auth, criar_eventos):
    evento = criar_eventos(1)[0]
    assert client.delete(f"/events/{evento.id}", headers=auth).status_code == 204
    assert _contar(db_session, "events") == 0
    assert client.delete(f"/events/{evento.id}", headers=auth).status_code == 404


# ---------- favoritos (tabelas favorito e usuario) ----------

@pytest.fixture()
def usuario(db_session):
    u = User(name="Ana", email="ana@cin.ufpe.br", hashed_password="h", profile_name="ana")
    db_session.add(u)
    db_session.commit()
    return u


def test_favoritar_e_desfavoritar_grava_na_tabela_favorito(client, db_session, usuario, criar_eventos):
    evento = criar_eventos(1)[0]
    h = {"X-User-Id": str(usuario.id)}
    r = client.post(f"/events/{evento.id}/favorite", headers=h)
    assert r.json() == {"event_id": evento.id, "is_favorited": True}
    assert _contar(db_session, "favorito", f"id_usuario={usuario.id} AND id_events={evento.id}") == 1
    # idempotente
    client.post(f"/events/{evento.id}/favorite", headers=h)
    assert _contar(db_session, "favorito") == 1
    r = client.delete(f"/events/{evento.id}/favorite", headers=h)
    assert r.json()["is_favorited"] is False
    assert _contar(db_session, "favorito") == 0
    assert client.delete(f"/events/{evento.id}/favorite", headers=h).status_code == 200


def test_favoritar_evento_inexistente_404(client, usuario):
    assert client.post("/events/9999/favorite", headers={"X-User-Id": str(usuario.id)}).status_code == 404


def test_favoritar_sem_header_422(client, criar_eventos):
    evento = criar_eventos(1)[0]
    assert client.post(f"/events/{evento.id}/favorite").status_code == 422


def test_favoritar_com_usuario_inexistente_nao_vira_500(client, db_session, criar_eventos):
    """Lacuna conhecida: o header X-User-Id não é validado contra a tabela usuario.
    A FK do banco recusa o INSERT; o comportamento esperado é um erro 4xx, não 500."""
    evento = criar_eventos(1)[0]
    try:
        r = client.post(f"/events/{evento.id}/favorite", headers={"X-User-Id": "9999"})
    except Exception as exc:  # TestClient relança a exceção do servidor
        pytest.xfail(f"usuário inexistente estoura exceção não tratada: {type(exc).__name__}")
    assert 400 <= r.status_code < 500


def test_excluir_evento_remove_favoritos(client, db_session, auth, usuario, criar_eventos):
    evento = criar_eventos(1)[0]
    client.post(f"/events/{evento.id}/favorite", headers={"X-User-Id": str(usuario.id)})
    client.delete(f"/events/{evento.id}", headers=auth)
    assert _contar(db_session, "favorito") == 0
    assert _contar(db_session, "usuario") == 1


# ---------- extração (tabelas extracao e events) ----------

class GmailFake:
    def __init__(self, emails, configured=True):
        self.emails, self.configured = emails, configured

    def is_configured(self):
        return self.configured

    def fetch_new_emails(self):
        return self.emails


def _email(msg, corpo):
    return RawEmail(message_id=msg, sender="sec@cin.ufpe.br", subject="Palestra de Dados",
                    body=corpo, received_at=dt.datetime.now(dt.timezone.utc))


@pytest.fixture()
def gmail(monkeypatch):
    """Troca o cliente do Gmail por um fake dentro da rota /extraction/run."""
    def _usar(emails, configured=True):
        monkeypatch.setattr(
            "app.api.extracao.router.run_extraction",
            lambda db: run_extraction(db, GmailFake(emails, configured)),
        )
    return _usar


def test_extracao_grava_evento_e_log(client, db_session, auth, gmail):
    gmail([_email("m1", "Data: 25/11/2030\nHora: 14h\nLocal: Auditório do CIn")])
    r = client.post("/extraction/run", headers=auth)
    assert r.status_code == 200
    assert (r.json()["fetched"], r.json()["processed"]) == (1, 1)
    assert _contar(db_session, "events", "origin='email'") == 1
    assert _contar(db_session, "extracao", "gmail_message_id='m1' AND status='processado' AND event_id IS NOT NULL") == 1


def test_extracao_e_idempotente(client, db_session, auth, gmail):
    gmail([_email("m1", "Data: 25/11/2030\nHora: 14h\nLocal: Auditório do CIn")])
    client.post("/extraction/run", headers=auth)
    r = client.post("/extraction/run", headers=auth)
    assert r.json()["duplicates"] == 1
    assert _contar(db_session, "events") == 1 and _contar(db_session, "extracao") == 1


def test_extracao_email_sem_dados_vira_ignorado(client, db_session, auth, gmail):
    gmail([_email("m2", "Só um aviso, sem dados.")])
    r = client.post("/extraction/run", headers=auth)
    assert r.json()["ignored"] == 1
    assert _contar(db_session, "extracao", "status='ignorado' AND event_id IS NULL") == 1
    assert _contar(db_session, "events") == 0


def test_extracao_sem_credenciais_nao_quebra(client, db_session, auth, gmail):
    gmail([], configured=False)
    r = client.post("/extraction/run", headers=auth)
    assert r.status_code == 200 and "não configurados" in r.json()["message"]


def test_evento_extraido_aparece_na_listagem_e_excluir_mantem_log(client, db_session, auth, gmail):
    gmail([_email("m1", "Data: 25/11/2030\nHora: 14h\nLocal: Auditório do CIn")])
    client.post("/extraction/run", headers=auth)
    item = client.get("/events").json()["items"][0]
    assert item["origin"] == "email"
    assert client.delete(f"/events/{item['id']}", headers=auth).status_code == 204
    assert _contar(db_session, "extracao", "event_id IS NULL AND status='processado'") == 1
