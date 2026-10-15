"""Orquestração da extração automática de e-mails.

Fluxo:
1. Busca novas mensagens na caixa institucional (Gmail API).
2. Para cada e-mail ainda não processado (idempotência por message_id):
   - parse estruturado OK → cria Event (origem "email") + log "processado";
   - e-mail sem dados obrigatórios → log "ignorado" com erro registrado;
   - erro inesperado → log "erro".

Critério de aceite do Gherkin: "então o sistema extrai ... e insere o evento no
banco"; "e-mail sem dados obrigatórios → ignorado + log de erro".
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.extraction_log import ExtractionLog
from app.repositories import event_repository, extraction_log_repository
from app.services.extracao_email.gmail_client import GmailClient, RawEmail
from app.services.extracao_email.parser import InsufficientDataError, parse_email


@dataclass
class ExtractionSummary:
    """Resultado de um ciclo de extração — usado no endpoint e no log do job."""

    fetched: int = 0
    processed: int = 0
    ignored: int = 0
    errors: int = 0
    duplicates: int = 0
    message: str = ""


def run_extraction(db: Session, client: GmailClient | None = None) -> ExtractionSummary:
    """Executa um ciclo completo de extração e persistência de eventos."""
    summary = ExtractionSummary()
    if client is None:
        client = GmailClient()

    if not client.is_configured():
        summary.message = "extração não executada: credenciais/token do Gmail não configurados"
        return summary

    try:
        emails = client.fetch_new_emails()
    except Exception as exc:  # rede/quota — retentativa é a US 4.6 (fora deste escopo)
        summary.message = f"falha ao buscar e-mails: {exc}"
        return summary

    summary.fetched = len(emails)
    for raw in emails:
        if extraction_log_repository.get_by_message_id(db, raw.message_id):
            summary.duplicates += 1
            continue
        _process_one(db, raw, summary)
    return summary


def _process_one(db: Session, raw: RawEmail, summary: ExtractionSummary) -> None:
    try:
        parsed = parse_email(raw.subject, raw.body)
    except InsufficientDataError as exc:
        log = ExtractionLog(
            gmail_message_id=raw.message_id,
            source_email=raw.sender,
            status="ignorado",
            error_message=f"e-mail sem dados obrigatórios: {', '.join(exc.missing)}",
        )
        extraction_log_repository.create(db, log)
        summary.ignored += 1
        return
    except Exception as exc:
        log = ExtractionLog(
            gmail_message_id=raw.message_id,
            source_email=raw.sender,
            status="erro",
            error_message=str(exc)[:500],
        )
        extraction_log_repository.create(db, log)
        summary.errors += 1
        return

    event = Event(
        title=parsed.title,
        description=parsed.description or parsed.title,
        date=parsed.date,
        time=parsed.time,
        location=parsed.location,
        event_type=parsed.event_type,
        registration_link=parsed.registration_link,
        status="active",
        origin="email",
    )
    event = event_repository.create(db, event)

    log = ExtractionLog(
        gmail_message_id=raw.message_id,
        source_email=raw.sender,
        status="processado",
        extracted_data=json.dumps(asdict(parsed), default=str, ensure_ascii=False),
        event_id=event.id,
    )
    extraction_log_repository.create(db, log)
    summary.processed += 1