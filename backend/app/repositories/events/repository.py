from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.events.models import Event, Favorite


def create(db: Session, event: Event) -> Event:
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_active(db: Session) -> list[Event]:
    return db.query(Event).filter(Event.status == "active").all()


def get_by_id(db: Session, event_id: int) -> Event | None:
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
    stmt = select(Favorite).where(
        Favorite.user_id == user_id, Favorite.event_id == event_id
    )
    return db.scalars(stmt).one_or_none()


def list_favorites_by_user(db: Session, user_id: int) -> list[Favorite]:
    """Lista os favoritos de um usuário."""
    stmt = select(Favorite).where(Favorite.user_id == user_id)
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
