"""Testes de regressão da Fase 2 — correções dos defeitos da Parte B (Back-end).

Cobre os defeitos levantados na auditoria do roteiro oficial:
- DEF-001 (BE-024): registration_link > 500 chars → 422 (POST e PUT)
- DEF-002 (BE-054): event_id fora do range int4 (2147483648) → 404 sem 500
- DEF-003 (BE-077): X-User-Id fora do range int4 (99999999999) → 404/200 sem 500
- DEF-004 (BE-161): GET /extraction/alerts?limit=-1 / 0 / 1000 → 422 sem 500
- DEF-005 (BE-120): e-mail com data no passado via parser é descartado (extracao_incompleta)
- DEF-006 (BE-089/090): prefixo "Divulgação:", título > 200 truncado, link entre parênteses e link > 500 descartado
- DEF-007 (BE-136): falha em event_repository.create faz rollback, registra erro e segue o lote
- DEF-008 (BE-041): GET /events não retorna eventos vencidos (ontem), mas mantém hoje e multi-dia
- DEF-010 (BE-005): login aceita e-mail em maiúsculas e com espaços
- DEF-011 (BE-084): parser extrai "19 horas" corretamente
"""

import datetime as dt

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.core.security import create_access_token, hash_password
from app.database import get_db
from app.main import app
from app.models.event import Event
from app.models.extraction_log import ExtractionLog
from app.repositories import user_repository
from app.services.events.cleanup_service import LOCAL_TZ
from app.services.extracao_email import extraction_service, parser
from app.services.extracao_email.gmail_client import RawEmail

FUTURO = (dt.datetime.now(LOCAL_TZ).date() + dt.timedelta(days=30)).isoformat()


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def admin_headers(db_session):
    user_repository.create(
        db_session,
        name="Admin",
        email="admin@cin.ufpe.br",
        hashed_password=hash_password("123456"),
        profile_name="admin",
        is_admin=True,
    )
    return {"Authorization": f"Bearer {create_access_token({'sub': 'admin@cin.ufpe.br'})}"}


def _payload(**extra):
    dados = {
        "title": "Palestra de IA",
        "description": "Descrição completa",
        "date": FUTURO,
        "time": "19:00:00",
        "location": "Auditório do CIn",
        "event_type": "Palestra",
        "registration_link": "https://cin.ufpe.br/inscricao",
    }
    dados.update(extra)
    return dados


class _GmailFake:
    def __init__(self, emails):
        self._emails = emails

    def is_configured(self):
        return True

    def fetch_new_emails(self):
        return list(self._emails)


class _GeminiOff:
    def is_configured(self):
        return False


def _raw(mid, body, subject="Palestra de IA"):
    return RawEmail(
        message_id=mid,
        sender="sec@cin.ufpe.br",
        subject=subject,
        body=body,
        received_at=dt.datetime.now(dt.timezone.utc),
    )


# ---------- DEF-010 (BE-005): normalização de e-mail no login ----------

@pytest.mark.parametrize("email", ["ADMIN@CIN.UFPE.BR", "  Admin@CIn.UFPE.br  "])
def test_login_aceita_email_maiusculo_e_com_espacos(client, admin_headers, email):
    r = client.post("/auth/login", json={"email": email, "password": "123456"})
    assert r.status_code == 200
    assert r.json()["token"]


# ---------- DEF-001 (BE-024): registration_link > 500 chars → 422 ----------

def test_post_e_put_rejeitam_registration_link_maior_que_500(client, admin_headers, criar_eventos):
    link_501 = "https://a.com/" + ("x" * 487)
    assert len(link_501) == 501
    assert client.post("/events", json=_payload(registration_link=link_501), headers=admin_headers).status_code == 422

    evento = criar_eventos(1)[0]
    assert client.put(f"/events/{evento.id}", json=_payload(registration_link=link_501), headers=admin_headers).status_code == 422


# ---------- DEF-002 (BE-054) e DEF-003 (BE-077): IDs acima de int4 ----------

@pytest.mark.parametrize("bad_id", ["0", "-1", "2147483648", "99999999999"])
def test_event_id_fora_do_int4_nao_gera_500(client, admin_headers, bad_id):
    assert client.get(f"/events/{bad_id}").status_code == 404
    assert client.put(f"/events/{bad_id}", json=_payload(), headers=admin_headers).status_code == 404
    assert client.delete(f"/events/{bad_id}", headers=admin_headers).status_code == 404


@pytest.mark.parametrize("bad_uid", ["0", "-1", "99999999999"])
def test_x_user_id_fora_do_int4_nao_gera_500(client, criar_eventos, bad_uid):
    evento = criar_eventos(1)[0]
    assert client.post(f"/events/{evento.id}/favorite", headers={"X-User-Id": bad_uid}).status_code == 404
    assert client.delete(f"/events/{evento.id}/favorite", headers={"X-User-Id": bad_uid}).status_code == 200


# ---------- DEF-004 (BE-161): limit inválido em /extraction/alerts ----------

@pytest.mark.parametrize("limit,esperado", [("1", 200), ("0", 422), ("-1", 422), ("1000", 422), ("abc", 422)])
def test_extraction_alerts_valida_limit(client, admin_headers, limit, esperado):
    r = client.get(f"/extraction/alerts?limit={limit}", headers=admin_headers)
    assert r.status_code == esperado


# ---------- DEF-008 (BE-041): GET /events oculta eventos expirados ----------

def test_listagem_publica_oculta_evento_de_ontem_e_mantem_hoje_e_multidia(client, db_session):
    hoje = dt.datetime.now(LOCAL_TZ).date()
    ontem = hoje - dt.timedelta(days=1)
    amanha = hoje + dt.timedelta(days=1)
    db_session.add_all([
        Event(title="Expirado Ontem", description="D", date=ontem, time=dt.time(10, 0),
              location="CIn", event_type="Palestra", registration_link="https://x.com", status="active", origin="manual"),
        Event(title="Evento Hoje", description="D", date=hoje, time=dt.time(10, 0),
              location="CIn", event_type="Palestra", registration_link="https://x.com", status="active", origin="manual"),
        Event(title="Multi-dia Ativo", description="D", date=ontem, time=dt.time(9, 0),
              end_date=amanha, end_time=dt.time(18, 0),
              location="CIn", event_type="Hackathon", registration_link="https://x.com", status="active", origin="manual"),
    ])
    db_session.commit()

    corpo = client.get("/events").json()
    titulos = [e["title"] for e in corpo["items"]]
    assert "Expirado Ontem" not in titulos
    assert set(titulos) == {"Evento Hoje", "Multi-dia Ativo"}
    assert corpo["total_pages"] == 1


# ---------- DEF-006 e DEF-011 (BE-084, BE-089, BE-090): parser ----------

def test_parser_extrai_19_horas_prefixo_divulgacao_e_limites():
    assert parser._extract_time("O evento será às 19 horas no auditório.") == dt.time(19, 0)
    assert parser._extract_title("Fwd: RE: [CIn] Divulgação: Workshop de React", "") == "Workshop de React"
    assert len(parser._extract_title("A" * 250, "")) == 200
    assert parser._first_link("", "Inscreva-se em (https://cin.ufpe.br/x), ou mailto:a@b.com") == "https://cin.ufpe.br/x"
    assert parser._first_link("", "Link: https://cin.ufpe.br/" + ("z" * 600)) == ""


# ---------- DEF-005 (BE-120): parser descarta data no passado ----------

def test_parser_estruturado_descarta_evento_no_passado(db_session):
    email_passado = _raw("f14", "Data: 25/11/2025\nHora: 14h\nLocal: Auditório do CIn", "Evento 2025")
    resumo = extraction_service.run_extraction(db_session, _GmailFake([email_passado]), _GeminiOff())

    assert resumo.processed == 0
    assert resumo.discarded == 1
    assert db_session.query(Event).count() == 0
    log = db_session.query(ExtractionLog).one()
    assert log.status == extraction_service.STATUS_EXTRACAO_INCOMPLETA
    assert "data_no_passado" in (log.error_message or "")


# ---------- DEF-007 (BE-136): rollback em falha de persistência ----------

def test_falha_de_persistencia_faz_rollback_e_processa_proximo_email(db_session, monkeypatch):
    d30 = (dt.datetime.now(LOCAL_TZ).date() + dt.timedelta(days=30)).strftime("%d/%m/%Y")
    e1 = _raw("b1", f"Data: {d30}\nHora: 14h\nLocal: CIn", "Primeiro")
    e2 = _raw("b2", f"Data: {d30}\nHora: 15h\nLocal: CIn", "Segundo")

    original_create = extraction_service.event_repository.create
    chamadas = {"n": 0}

    def _create_falha_primeiro(db, ev):
        chamadas["n"] += 1
        if chamadas["n"] == 1:
            raise IntegrityError("stmt", {}, Exception("falha simulada"))
        return original_create(db, ev)

    monkeypatch.setattr(extraction_service.event_repository, "create", _create_falha_primeiro)

    resumo = extraction_service.run_extraction(db_session, _GmailFake([e1, e2]), _GeminiOff())

    assert resumo.errors == 1
    assert resumo.processed == 1
    assert db_session.query(Event).one().title == "Segundo"
    statuses = {log.gmail_message_id: log.status for log in db_session.query(ExtractionLog).all()}
    assert statuses == {"b1": "erro", "b2": "processado"}
