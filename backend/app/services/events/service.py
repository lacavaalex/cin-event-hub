import datetime as dt
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models.events.models import Event
from app.repositories.events import repository
from app.schemas.events.schemas import EventUpdate

# "Hoje" precisa ser o de Recife: o servidor pode rodar em UTC e, à noite,
# já estar no dia seguinte.
LOCAL_TZ = ZoneInfo("America/Recife")


class EventNotFoundError(Exception):
    """Nenhum evento com o ID informado."""


class PastEventDateError(Exception):
    """Tentativa de mover o evento para uma data que já passou."""


def get_event(db: Session, event_id: int) -> Event:
    event = repository.get_by_id(db, event_id)
    if event is None:
        raise EventNotFoundError(event_id)
    return event


def update_event(db: Session, event_id: int, payload: EventUpdate) -> Event:
    event = get_event(db, event_id)

    # Só bloqueia data passada quando a data está sendo ALTERADA. Assim, é
    # possível corrigir o título de um evento de hoje sem ser barrado.
    today = dt.datetime.now(LOCAL_TZ).date()
    if payload.date != event.date and payload.date < today:
        raise PastEventDateError(payload.date)

    changes = {
        "title": payload.title,
        "description": payload.description,
        "date": payload.date,
        "time": payload.time,
        "location": payload.location,
        "event_type": payload.event_type.value,
        "registration_link": str(payload.registration_link),  
    }
    return repository.update(db, event, changes)


def delete_event(db: Session, event_id: int) -> None:
    """Remove o evento do sistema (US 2.3)."""
    event = get_event(db, event_id)
    repository.delete(db, event)
    