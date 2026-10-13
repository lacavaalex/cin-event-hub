"""Repositório de persistência de favoritos (US 6.1)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.events.models import Favorite


def get(db: Session, user_id: int, event_id: int) -> Favorite | None:
    """Busca o favorito de um usuário para um evento, se existir."""
    stmt = select(Favorite).where(
        Favorite.user_id == user_id, Favorite.event_id == event_id
    )
    return db.scalars(stmt).one_or_none()


def list_by_user(db: Session, user_id: int) -> list[Favorite]:
    """Lista todos os favoritos de um usuário."""
    stmt = select(Favorite).where(Favorite.user_id == user_id)
    return list(db.scalars(stmt).all())


def create(db: Session, user_id: int, event_id: int) -> Favorite:
    """Cria um favorito para um usuário e evento."""
    favorite = Favorite(user_id=user_id, event_id=event_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


def delete(db: Session, favorite: Favorite) -> None:
    """Remove um favorito existente."""
    db.delete(favorite)
    db.commit()
