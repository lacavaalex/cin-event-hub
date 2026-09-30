"""Repositório de eventos: acesso direto ao banco (camada de dados).

Só conhece o ORM e a tabela `events` — não conhece regra de negócio nem
HTTP. Devolve `None` quando o evento não existe; quem decide o que fazer
com isso (levantar exceção, retornar 404...) é a camada de serviço.
"""
from sqlalchemy.orm import Session

from app.models.events.models import Event


def get_by_id(db: Session, event_id: int) -> Event | None:
    """Busca um evento pelo ID. Usado tanto na edição quanto na exclusão."""
    return db.get(Event, event_id)


def update(db: Session, event: Event, changes: dict) -> Event:
    """Aplica os campos de `changes` no evento já carregado e persiste (US 2.2)."""
    for field, value in changes.items():
        setattr(event, field, value)

    db.commit()  # persiste no PostgreSQL
    db.refresh(event)  # recarrega, trazendo o updated_at gerado pelo banco
    return event


def delete(db: Session, event: Event) -> None:
    """Remove o evento já carregado (US 2.3). Exclusão definitiva, não lógica."""
    db.delete(event)
    db.commit()
