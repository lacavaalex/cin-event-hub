"""Testes da listagem administrativa de eventos (US 2.4).

Cobrem os critérios da rota ``GET /events/admin``:
- exige autenticação de administrador;
- lista todos os eventos cadastrados, inclusive os vencidos;
- sinaliza com ``is_expired`` os eventos cuja data limite já passou.
"""

import datetime as dt

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password
from app.database import get_db
from app.main import app
from app.models.event import Event
from app.repositories import user_repository
from app.services.events.cleanup_service import LOCAL_TZ


def _criar_evento(
    db: Session,
    title: str,
    date: dt.date,
    *,
    time: dt.time = dt.time(10, 0),
    end_date: dt.date | None = None,
    status: str = "active",
) -> Event:
    event = Event(
        title=title,
        description=f"Descrição de {title}",
        date=date,
        time=time,
        end_date=end_date,
        end_time=dt.time(18, 0) if end_date else None,
        location="CIn - Auditório",
        event_type="Palestra",
        registration_link="https://cin.ufpe.br/inscricao",
        status=status,
        origin="manual",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@pytest.fixture()
def admin_client(db_session: Session):
    # get_current_admin confere no banco: o admin precisa existir em ``usuario``.
    user_repository.create(
        db_session,
        name="Admin",
        email="admin@cin.ufpe.br",
        hashed_password=hash_password("123456"),
        profile_name="admin",
        is_admin=True,
    )
    app.dependency_overrides[get_db] = lambda: db_session
    client = TestClient(app)
    token = create_access_token({"sub": "admin@cin.ufpe.br"})
    try:
        yield client, {"Authorization": f"Bearer {token}"}
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_admin_events_requires_authentication():
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/events/admin")

    assert response.status_code in (401, 403)


def test_admin_events_lists_active_expired_and_inactive(admin_client, db_session: Session):
    hoje = dt.datetime.now(LOCAL_TZ).date()
    _criar_evento(
        db_session,
        "Evento futuro",
        hoje + dt.timedelta(days=10),
        time=dt.time(14, 30),
    )
    _criar_evento(
        db_session,
        "Evento vencido",
        hoje - dt.timedelta(days=10),
    )
    _criar_evento(
        db_session,
        "Evento inativo",
        hoje + dt.timedelta(days=5),
        status="inactive",
    )

    client, headers = admin_client
    response = client.get("/events/admin", headers=headers)

    assert response.status_code == 200
    events = {event["title"]: event for event in response.json()}
    assert set(events) == {"Evento futuro", "Evento vencido", "Evento inativo"}
    assert events["Evento futuro"]["is_expired"] is False
    assert events["Evento vencido"]["is_expired"] is True
    assert events["Evento inativo"]["is_expired"] is False


def test_admin_events_uses_end_date_to_determine_expiration(admin_client, db_session: Session):
    hoje = dt.datetime.now(LOCAL_TZ).date()
    _criar_evento(
        db_session,
        "Evento de vários dias",
        hoje - dt.timedelta(days=2),
        end_date=hoje + dt.timedelta(days=2),
    )

    client, headers = admin_client
    response = client.get("/events/admin", headers=headers)

    assert response.status_code == 200
    [event] = response.json()
    assert event["title"] == "Evento de vários dias"
    assert event["is_expired"] is False


def test_admin_events_are_sorted_by_date_and_time(admin_client, db_session: Session):
    hoje = dt.datetime.now(LOCAL_TZ).date()
    _criar_evento(db_session, "Segundo", hoje + dt.timedelta(days=2))
    _criar_evento(db_session, "Primeiro", hoje + dt.timedelta(days=1), time=dt.time(9, 0))
    _criar_evento(db_session, "Terceiro", hoje + dt.timedelta(days=2), time=dt.time(8, 0))

    client, headers = admin_client
    response = client.get("/events/admin", headers=headers)

    assert response.status_code == 200
    titles = [event["title"] for event in response.json()]
    assert titles == ["Primeiro", "Terceiro", "Segundo"]
