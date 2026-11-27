import datetime as dt

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.events.models import Event, Favorite

_PG_INT4_MAX = 2_147_483_647


def _is_valid_pg_id(value: int) -> bool:
    return 1 <= value <= _PG_INT4_MAX


def create(db: Session, event: Event) -> Event:
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_active(db: Session) -> list[Event]:
    return db.query(Event).filter(Event.status == "active").all()


def list_all(db: Session) -> list[Event]:
    """Lista todos os eventos cadastrados, inclusive os já expirados (US 2.4)."""
    return db.query(Event).order_by(Event.date, Event.time, Event.id).all()


def get_by_id(db: Session, event_id: int) -> Event | None:
    if not _is_valid_pg_id(event_id):
        return None
    return db.get(Event, event_id)


def update(db: Session, event: Event, changes: dict) -> Event:
    for field, value in changes.items():
        setattr(event, field, value)

    db.commit()  
    db.refresh(event) 
    return event


def delete(db: Session, event: Event) -> None:
    db.delete(event)
    db.commit()


def get_favorite(db: Session, user_id: int, event_id: int) -> Favorite | None:
    """Busca o favorito de um usuário para um evento, se existir."""
    if not (_is_valid_pg_id(user_id) and _is_valid_pg_id(event_id)):
        return None
    stmt = select(Favorite).where(
        Favorite.user_id == user_id, Favorite.event_id == event_id
    )
    return db.scalars(stmt).one_or_none()


def list_favorites_by_user(db: Session, user_id: int) -> list[Favorite]:
    """Lista os favoritos de um usuário."""
    if not _is_valid_pg_id(user_id):
        return []
    stmt = select(Favorite).where(Favorite.user_id == user_id)
    return list(db.scalars(stmt).all())


def list_favorite_events_by_user(
    db: Session,
    user_id: int,
    min_date: dt.date | None = None,
) -> list[Event]:
    """Lista os eventos ativos favoritados pelo usuário em ordem cronológica (US 6.2)."""
    if not _is_valid_pg_id(user_id):
        return []
    stmt = (
        select(Event)
        .join(Favorite, Favorite.event_id == Event.id)
        .where(Favorite.user_id == user_id, Event.status == "active")
    )
    if min_date is not None:
        stmt = stmt.where(func.coalesce(Event.end_date, Event.date) >= min_date)
    stmt = stmt.order_by(Event.date, Event.time, Event.id)
    return list(db.scalars(stmt).all())


def create_favorite(db: Session, user_id: int, event_id: int) -> Favorite:
    """Cria o favorito de um usuário para um evento."""
    favorite = Favorite(user_id=user_id, event_id=event_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


def delete_favorite(db: Session, favorite: Favorite) -> None:
    """Remove um favorito existente."""
    db.delete(favorite)
    db.commit()
