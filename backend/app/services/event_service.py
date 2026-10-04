"""Serviço de eventos — regras de negócio de criação (US 2.1) e listagem."""

import datetime as dt
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models.event import Event
from app.repositories import event_repository
from app.schemas.event import EventCreate

# Fuso horário local — o servidor pode rodar em UTC, mas a regra de data
# usa o horário de Recife (mesmo critério da branch develop_alb).
LOCAL_TZ = ZoneInfo("America/Recife")


class PastEventDateError(Exception):
    """Tentativa de criar evento com data no passado."""


def create_event(db: Session, payload: EventCreate) -> Event:
    """Cria um novo evento validando as regras de negócio.

    Cenários cobertos (Gherkin da US 2.1):
    - Criar evento com sucesso → persiste e retorna o evento
    - Campos obrigatórios vazios → o Pydantic já rejeita antes de chegar aqui
    - Data no passado → levanta PastEventDateError
    """
    today = dt.datetime.now(LOCAL_TZ).date()
    if payload.date < today:
        raise PastEventDateError(payload.date)

    event = Event(
        title=payload.title,
        description=payload.description,
        date=payload.date,
        time=payload.time,
        location=payload.location,
        event_type=payload.event_type.value,
        registration_link=str(payload.registration_link),
        status="active",
        origin="manual",
    )
    return event_repository.create(db, event)


def list_events(db: Session) -> list[Event]:
    """Retorna todos os eventos ativos (US 3.1)."""
    return event_repository.get_all(db)
