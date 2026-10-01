"""Repositório de eventos — acesso direto ao banco de dados.

Mantém compatibilidade com o repositório da branch develop_alb (Albert),
adicionando as operações de criação (US 2.1) e listagem (US 3.1).
"""

from sqlalchemy.orm import Session

from app.models.event import Event


def create(db: Session, event: Event) -> Event:
    """Persiste um novo evento no banco (US 2.1)."""
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_all(db: Session) -> list[Event]:
    """Retorna todos os eventos ativos ordenados por data (US 3.1)."""
    return db.query(Event).filter(Event.status == "active").order_by(Event.date).all()


def get_by_id(db: Session, event_id: int) -> Event | None:
    """Busca um evento pelo ID."""
    return db.get(Event, event_id)
