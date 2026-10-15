"""Job agendado de extração de e-mails.

O APScheduler é importado por dentro das funções para que a aplicação rode o
restante do backend (ou os testes) mesmo se a dependência não estiver instalada.
Quando ``EXTRACTION_ENABLED`` for verdadeiro e houver credenciais, um job de
intervalo começa no lifespan do FastAPI e executa ``run_extraction``.
"""

from __future__ import annotations

import logging

from app.core.config import EXTRACTION_ENABLED, EXTRACTION_INTERVAL_MINUTES
from app.database.database import SessionLocal
from app.services.extracao_email.extraction_service import run_extraction

logger = logging.getLogger(__name__)

_LOCAL_TZ = "America/Recife"

_scheduler = None


def start_scheduler() -> None:
    """Inicia o agendador em background (chamado no lifespan do FastAPI)."""
    global _scheduler

    if not EXTRACTION_ENABLED:
        logger.info("Extração de e-mails desativada (EXTRACTION_ENABLED=false).")
        return

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
    except ImportError:
        logger.warning(
            "APScheduler não instalado — pip install -r requirements.txt. "
            "A extração automática não será agendada."
        )
        return

    scheduler = BackgroundScheduler(timezone=_LOCAL_TZ)
    scheduler.add_job(
        _run_job,
        "interval",
        minutes=EXTRACTION_INTERVAL_MINUTES,
        id="extracao_de_emails",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.start()
    _scheduler = scheduler
    logger.info(
        "Extração de e-mails agendada a cada %s minutos.", EXTRACTION_INTERVAL_MINUTES
    )


def shutdown_scheduler() -> None:
    """Encerra o agendador (chamado no lifespan)."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None


def _run_job() -> None:
    db = SessionLocal()
    try:
        summary = run_extraction(db)
        logger.info(
            "Execução da extração: %s novos | %s ignorados | %s erros | %s duplicatas",
            summary.processed,
            summary.ignored,
            summary.errors,
            summary.duplicates,
        )
        if summary.message:
            logger.warning(summary.message)
    except Exception:  # job nunca deve derrubar o agendador
        logger.exception("Falha não tratada na extração agendada.")
    finally:
        db.close()