"""Serviço de expiração e limpeza de eventos expirados (US 5.1 / 5.2).

Regras de negócio:
- US 5.1: Identificação e exclusão de eventos com data limite ultrapassada.
  * Evento com data < reference_date é removido do banco / listagem.
  * Mensagem de log é registrada para cada evento removido.
  * Eventos com data futura permanecem visíveis.
- US 5.2: Relatório de limpeza estruturado após a execução autônoma/agendada.
"""

from __future__ import annotations

import datetime as dt
import logging
from dataclasses import dataclass, field
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.extraction_log import ExtractionLog
from app.repositories import event_repository

logger = logging.getLogger(__name__)

LOCAL_TZ = ZoneInfo("America/Recife")


@dataclass
class CleanupReport:
    """Relatório estruturado da rotina de limpeza de eventos expirados."""

    executed_at: dt.datetime
    reference_date: dt.date
    expired_count: int = 0
    deleted_event_ids: list[int] = field(default_factory=list)
    deleted_titles: list[str] = field(default_factory=list)
    message: str = ""


class FutureReferenceDateError(ValueError):
    """Data de referência no futuro não é permitida para limpeza de eventos."""


def is_event_expired(event: Event, reference_date: dt.date | None = None) -> bool:
    """Verifica se um evento está expirado em relação a uma data de referência (US 5.1).

    A data limite do evento é a sua data de término (end_date), quando informada,
    ou a data de início (date) para eventos de um único dia.
    """
    if reference_date is None:
        reference_date = dt.datetime.now(LOCAL_TZ).date()
    limit_date = event.end_date if getattr(event, "end_date", None) is not None else event.date
    return limit_date < reference_date


def get_expired_events(
    db: Session,
    reference_date: dt.date | None = None,
) -> list[Event]:
    """Retorna todos os eventos cuja data limite já passou (US 5.1)."""
    if reference_date is None:
        reference_date = dt.datetime.now(LOCAL_TZ).date()

    return event_repository.get_expired_events(db, reference_date)


def clean_expired_events(
    db: Session,
    reference_date: dt.date | None = None,
    allow_future: bool = False,
) -> CleanupReport:
    """Executa a limpeza de eventos com data limite ultrapassada (US 5.1 / 5.2).

    Para cada evento com data limite < reference_date:
    1. Desvincula logs de extração associados para manter integridade referencial.
    2. Exclui o evento do banco de dados (removendo-o da listagem).
    3. Registra mensagem de log informando a exclusão do evento.
    4. Gera o relatório com os detalhes dos eventos removidos.
    """
    now = dt.datetime.now(LOCAL_TZ)
    today = now.date()
    if reference_date is None:
        reference_date = today

    if reference_date > today and not allow_future:
        raise FutureReferenceDateError(
            f"A data de referência ({reference_date}) não pode ser futura."
        )

    expired_events = get_expired_events(db, reference_date)

    deleted_ids: list[int] = []
    deleted_titles: list[str] = []

    for event in expired_events:
        event_id = event.id
        event_title = event.title
        event_date = event.date

        # Desvincula registros de log de extração de e-mails para preservar histórico
        db.query(ExtractionLog).filter(ExtractionLog.event_id == event_id).update(
            {"event_id": None}
        )

        db.delete(event)
        deleted_ids.append(event_id)
        deleted_titles.append(event_title)

        # Critério Gherkin: "E uma mensagem de log é registrada"
        logger.info(
            "Evento expirado removido automaticamente: ID=%s, título='%s', data=%s (referência: %s)",
            event_id,
            event_title,
            event_date,
            reference_date,
        )

    if deleted_ids:
        db.commit()

    count = len(deleted_ids)
    if count > 0:
        msg = f"Limpeza concluída com sucesso: {count} evento(s) expirado(s) removido(s)."
    else:
        msg = "Limpeza concluída: nenhum evento expirado encontrado."

    logger.info(msg)

    return CleanupReport(
        executed_at=now,
        reference_date=reference_date,
        expired_count=count,
        deleted_event_ids=deleted_ids,
        deleted_titles=deleted_titles,
        message=msg,
    )
