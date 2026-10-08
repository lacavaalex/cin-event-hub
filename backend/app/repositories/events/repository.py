from sqlalchemy.orm import Session
from app.models.events.models import Event


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
