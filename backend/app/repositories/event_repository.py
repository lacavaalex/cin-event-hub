"""Repositório de eventos — acesso direto ao banco de dados.

Mantém compatibilidade com o repositório da branch develop_alb (Albert),
adicionando as operações de criação (US 2.1) e listagem (US 3.1).
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.event import Event


def create(db: Session, event: Event) -> Event:
    """Persiste um novo evento no banco (US 2.1)."""
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_all(db: Session, limit: int = 20, offset: int = 0) -> list[Event]:
    """Retorna uma página de eventos ativos em ordem cronológica (US 3.1, IESI-71).

    ``limit`` e ``offset`` viram LIMIT/OFFSET na query do PostgreSQL. A ordem é
    data, hora e id: o id desempata eventos no mesmo horário para que, entre uma
    página e outra, nenhum evento se repita ou fique de fora (sem ordem total,
    o PostgreSQL pode devolver linhas empatadas em qualquer ordem).
    """
    return (
        db.query(Event)
        .filter(Event.status == "active")
        .order_by(Event.date, Event.time, Event.id)
        .limit(limit)
        .offset(offset)
        .all()
    )


def count_active(db: Session) -> int:
    """Conta os eventos ativos (base do total de páginas da listagem, IESI-70)."""
    return db.query(func.count(Event.id)).filter(Event.status == "active").scalar()


def get_by_id(db: Session, event_id: int) -> Event | None:
    """Busca um evento pelo ID."""
    return db.get(Event, event_id)
