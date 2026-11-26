"""Repositório dos logs de extração de e-mails (US 4.1)."""

import datetime as dt
from collections.abc import Sequence

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.extraction_log import ExtractionLog


def create(db: Session, log: ExtractionLog) -> ExtractionLog:
    """Persiste um novo log de extração."""
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_by_message_id(db: Session, gmail_message_id: str) -> ExtractionLog | None:
    """Busca o log pela mensagem do Gmail — garante que a varredura seja idempotente."""
    return (
        db.query(ExtractionLog)
        .filter(ExtractionLog.gmail_message_id == gmail_message_id)
        .first()
    )


def list_by_status(
    db: Session, status: str, limit: int = 50
) -> list[ExtractionLog]:
    return (
        db.query(ExtractionLog)
        .filter(ExtractionLog.status == status)
        .order_by(ExtractionLog.created_at.desc(), ExtractionLog.id.desc())
        .limit(limit)
        .all()
    )


def list_by_statuses(
    db: Session, statuses: Sequence[str], limit: int = 50
) -> list[ExtractionLog]:
    """Lista logs cujo status está em ``statuses`` (alertas da US 4.2 + US 4.4)."""
    return (
        db.query(ExtractionLog)
        .filter(ExtractionLog.status.in_(list(statuses)))
        .order_by(ExtractionLog.created_at.desc(), ExtractionLog.id.desc())
        .limit(limit)
        .all()
    )


def unlink_event(db: Session, event_id: int) -> None:
    """Desvincula logs associados a um evento que será excluído (preserva histórico)."""
    (
        db.query(ExtractionLog)
        .filter(ExtractionLog.event_id == event_id)
        .update({"event_id": None})
    )


def count_by_status(db: Session) -> dict[str, int]:
    """Agrupa a contagem de logs por status (base do painel US 4.3)."""
    rows = (
        db.query(ExtractionLog.status, func.count(ExtractionLog.id))
        .group_by(ExtractionLog.status)
        .all()
    )
    return {status: int(total) for status, total in rows}


def get_last_created_at(db: Session) -> dt.datetime | None:
    """Retorna o timestamp do log de extração mais recente, se houver."""
    return db.query(func.max(ExtractionLog.created_at)).scalar()
