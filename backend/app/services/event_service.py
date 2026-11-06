"""Serviço de eventos — regras de negócio de criação (US 2.1) e listagem."""

import datetime as dt
import math
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models.event import Event
from app.repositories import event_repository
from app.schemas.event import EventCreate

# Fuso horário local — o servidor pode rodar em UTC, mas a regra de data
# usa o horário de Recife (mesmo critério da branch develop_alb).
LOCAL_TZ = ZoneInfo("America/Recife")

# Paginação da listagem (IESI-70): 20 eventos por página por padrão (critério da
# task). O teto evita que um page_size enorme anule o LIMIT da consulta.
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


@dataclass
class EventsPage:
    """Uma página de eventos e seus metadados."""

    items: list[Event]
    page: int
    total_pages: int


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


def list_events(
    db: Session, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE
) -> EventsPage:
    """Retorna uma página dos eventos ativos com os metadados de paginação (US 3.1).

    ``page`` começa em 1. Página além do total devolve ``items`` vazio, com
    ``total_pages`` correto, para o cliente saber onde parar.
    """
    offset = (page - 1) * page_size
    items = event_repository.get_all(db, limit=page_size, offset=offset)
    total = event_repository.count_active(db)
    return EventsPage(items=items, page=page, total_pages=math.ceil(total / page_size))
