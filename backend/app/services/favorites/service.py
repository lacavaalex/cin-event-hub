"""Serviço de favoritos (US 6.1)."""

from sqlalchemy.orm import Session

from app.models.events.models import Favorite
from app.repositories.events import repository as events_repository
from app.repositories.favorites import repository as favorites_repository
from app.schemas.events.schemas import FavoriteStatus


class EventNotFoundError(Exception):
    """Nenhum evento com o ID informado."""


def favorite_event(db: Session, user_id: int, event_id: int) -> FavoriteStatus:
    """Favorita um evento para o usuário de forma idempotente."""
    if events_repository.get_by_id(db, event_id) is None:
        raise EventNotFoundError(event_id)

    if favorites_repository.get(db, user_id, event_id) is None:
        favorites_repository.create(db, user_id, event_id)

    return FavoriteStatus(event_id=event_id, is_favorited=True)


def unfavorite_event(db: Session, user_id: int, event_id: int) -> FavoriteStatus:
    """Remove o favorito do usuário de forma idempotente."""
    existing = favorites_repository.get(db, user_id, event_id)
    if existing is not None:
        favorites_repository.delete(db, existing)

    return FavoriteStatus(event_id=event_id, is_favorited=False)
