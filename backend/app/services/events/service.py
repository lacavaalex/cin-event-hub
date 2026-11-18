import datetime as dt
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models.events.models import Event
from app.repositories import user_repository
from app.repositories.events import repository
from app.schemas.events.schemas import EventCreate, EventUpdate, FavoriteStatus

# "Hoje" precisa ser o de Recife: o servidor pode rodar em UTC e, à noite,
# já estar no dia seguinte.
LOCAL_TZ = ZoneInfo("America/Recife")


class EventNotFoundError(Exception):
    """Nenhum evento com o ID informado."""


class UserNotFoundError(Exception):
    """Nenhum usuário com o ID informado."""


class PastEventDateError(Exception):
    """Tentativa de mover o evento para uma data que já passou."""


def create_event(db: Session, payload: EventCreate) -> Event:
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
    return repository.create(db, event)


def list_events(db: Session) -> list[Event]:
    return repository.list_active(db)


def list_admin_events(db: Session) -> list[Event]:
    """Lista todos os eventos para o painel administrativo (US 2.4).

    Diferente da listagem pública, inclui eventos vencidos que ainda não foram
    removidos pela rotina de limpeza da US 5.1/5.2.
    """
    return repository.list_all(db)


def favorite_event(db: Session, user_id: int, event_id: int) -> FavoriteStatus:
    """Favorita um evento para o usuário de forma idempotente."""
    if repository.get_by_id(db, event_id) is None:
        raise EventNotFoundError(event_id)
    if user_repository.get_by_id(db, user_id) is None:
        raise UserNotFoundError(user_id)

    if repository.get_favorite(db, user_id, event_id) is None:
        repository.create_favorite(db, user_id, event_id)

    return FavoriteStatus(event_id=event_id, is_favorited=True)


def unfavorite_event(db: Session, user_id: int, event_id: int) -> FavoriteStatus:
    """Remove o favorito do usuário de forma idempotente."""
    existing = repository.get_favorite(db, user_id, event_id)
    if existing is not None:
        repository.delete_favorite(db, existing)

    return FavoriteStatus(event_id=event_id, is_favorited=False)


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
    