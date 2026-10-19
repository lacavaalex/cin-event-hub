"""Rotina agendada (CRON) para execução autônoma da limpeza na base de dados (US 5.2).

Configura o agendador em background (APScheduler) para executar periodicamente
a identificação e exclusão de eventos cuja data limite já passou (US 5.1).
Por padrão, executa diariamente às 03:00 (America/Recife) ou no intervalo configurado.
"""

from __future__ import annotations

import logging

from app.core.config import (
    CLEANUP_CRON_HOUR,
    CLEANUP_CRON_MINUTE,
    CLEANUP_ENABLED,
    CLEANUP_INTERVAL_MINUTES,
)
from app.database.database import SessionLocal
from app.services.events.cleanup_service import CleanupReport, clean_expired_events

logger = logging.getLogger(__name__)

_LOCAL_TZ = "America/Recife"
_scheduler = None


def start_cleanup_scheduler() -> None:
    """Inicia o agendador em background da rotina de limpeza (chamado no lifespan do FastAPI)."""
    global _scheduler

    if not CLEANUP_ENABLED:
        logger.info("Rotina de limpeza de eventos desativada (CLEANUP_ENABLED=false).")
        return

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        logger.warning(
            "APScheduler não instalado — pip install -r requirements.txt. "
            "A rotina de limpeza automática não será agendada."
        )
        return

    scheduler = BackgroundScheduler(timezone=_LOCAL_TZ)

    if CLEANUP_INTERVAL_MINUTES is not None:
        scheduler.add_job(
            run_cleanup_job,
            "interval",
            minutes=CLEANUP_INTERVAL_MINUTES,
            id="limpeza_eventos_expirados",
            replace_existing=True,
            max_instances=1,
        )
        logger.info(
            "Rotina de limpeza de eventos agendada a cada %s minutos.",
            CLEANUP_INTERVAL_MINUTES,
        )
    else:
        scheduler.add_job(
            run_cleanup_job,
            CronTrigger(
                hour=CLEANUP_CRON_HOUR,
                minute=CLEANUP_CRON_MINUTE,
                timezone=_LOCAL_TZ,
            ),
            id="limpeza_eventos_expirados",
            replace_existing=True,
            max_instances=1,
        )
        logger.info(
            "Rotina de limpeza de eventos agendada diariamente (CRON) às %02d:%02d (%s).",
            CLEANUP_CRON_HOUR,
            CLEANUP_CRON_MINUTE,
            _LOCAL_TZ,
        )

    scheduler.start()
    _scheduler = scheduler


def shutdown_cleanup_scheduler() -> None:
    """Encerra o agendador da rotina de limpeza (chamado no lifespan do FastAPI)."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None


def run_cleanup_job() -> CleanupReport | None:
    """Executa um ciclo da tarefa agendada de limpeza (US 5.2)."""
    db = SessionLocal()
    try:
        report = clean_expired_events(db)
        logger.info(
            "Relatório de limpeza gerado: executado em %s | referência %s | %d excluído(s)",
            report.executed_at,
            report.reference_date,
            report.expired_count,
        )
        return report
    except Exception:  # job nunca deve derrubar o agendador
        logger.exception("Falha não tratada na execução da rotina de limpeza agendada.")
        return None
    finally:
        db.close()
