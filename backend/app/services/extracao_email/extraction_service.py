"""Orquestração da extração automática de e-mails (US 4.1 + US 4.2 + US 4.4).

Fluxo por e-mail ainda não processado (idempotência por ``message_id``):

1. Parser estruturado (US 4.1). Se extrair os campos obrigatórios:
   - cria ``Event`` (``origin="email"``, ``status="active"``) + log "processado".
2. Se faltarem dados, cai no **fallback de IA** (US 4.2), quando o Gemini está
   configurado:
   - IA identifica evento e extrai os campos → **validação autónoma (US 4.4 /
     IESI-75)**: estrutura íntegra e data não passada → ``Event`` publicado
     (``status="active"``) + log "processado_ia"; caso contrário o evento é
     **silenciosamente descartado** + log "extracao_incompleta";
   - IA conclui que **não é evento** → log "ignorado";
   - IA confirma evento, mas faltam campos obrigatórios → descarte + log
     "extracao_incompleta" (contado em ``unprocessed``; alerta em
     ``GET /extraction/alerts``).
3. Se a IA **não** está configurada, mantém o comportamento da US 4.1 (sem dados
   obrigatórios → "ignorado").
4. Falhas inesperadas (incl. queda da API do Gemini) → log "erro".

Os registos "extracao_incompleta" alimentam o dashboard de monitorização
(US 4.3) — o consumidor do dashboard fica fora deste escopo.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.extraction_log import ExtractionLog
from app.repositories import event_repository, extraction_log_repository
from app.services.extracao_email.gmail_client import GmailClient, RawEmail
from app.services.extracao_email.parser import (
    InsufficientDataError,
    ParsedEvent,
    parse_email,
)
from app.services.ia_gemini.gemini_client import (
    GeminiClient,
    NotAnEventError,
    UnprocessableEventError,
)
from app.services.validacao import ValidationDecision, evaluate

STATUS_PROCESSADO = "processado"
STATUS_PROCESSADO_IA = "processado_ia"
STATUS_IGNORADO = "ignorado"
STATUS_NAO_PROCESSADO = "nao_processado"   # legado (pré-US 4.4) — ainda listado nos alertas
STATUS_EXTRACAO_INCOMPLETA = "extracao_incompleta"  # US 4.4: validação recusou
STATUS_ERRO = "erro"


@dataclass
class ExtractionSummary:
    """Resultado de um ciclo de extração — usado no endpoint e no log do job."""

    fetched: int = 0
    processed: int = 0      # extraídos pelo parser estruturado (US 4.1)
    processed_ia: int = 0   # extraídos pelo Gemini e publicados (US 4.2 + 4.4)
    ignored: int = 0
    unprocessed: int = 0    # IA não extraiu campos obrigatórios (alerta)
    discarded: int = 0      # validação autónoma descartou o evento (US 4.4)
    errors: int = 0
    duplicates: int = 0
    message: str = ""


def run_extraction(
    db: Session,
    client: GmailClient | None = None,
    gemini_client: GeminiClient | None = None,
) -> ExtractionSummary:
    """Executa um ciclo completo de extração e persistência de eventos."""
    summary = ExtractionSummary()
    if client is None:
        client = GmailClient()
    if gemini_client is None:
        gemini_client = GeminiClient()

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
        _process_one(db, raw, summary, gemini_client)
    return summary


def _process_one(
    db: Session,
    raw: RawEmail,
    summary: ExtractionSummary,
    gemini_client: GeminiClient,
) -> None:
    try:
        parsed = parse_email(raw.subject, raw.body)
    except InsufficientDataError:
        _fallback_ia(db, raw, summary, gemini_client)
        return
    except Exception as exc:
        _log(db, raw, STATUS_ERRO, error_message=_short(exc))
        summary.errors += 1
        return

    _persist(db, raw, parsed, summary, status="active", log_status=STATUS_PROCESSADO)
    summary.processed += 1


def _fallback_ia(
    db: Session,
    raw: RawEmail,
    summary: ExtractionSummary,
    gemini_client: GeminiClient,
) -> None:
    """US 4.2: tenta a IA para e-mails que o parser estruturado não entendeu."""
    if not gemini_client.is_configured():
        _log(
            db,
            raw,
            STATUS_IGNORADO,
            error_message="e-mail sem dados obrigatórios (IA desativada)",
        )
        summary.ignored += 1
        return

    try:
        parsed = gemini_client.extract_event(raw.subject, raw.body)
    except NotAnEventError:
        _log(db, raw, STATUS_IGNORADO, error_message="e-mail não classificado como evento")
        summary.ignored += 1
        return
    except UnprocessableEventError as exc:
        # US 4.4: extração incompleta → descarte silencioso + registo para o
        # dashboard (contado como "não processado" para o alerta da US 4.2).
        _log(
            db,
            raw,
            STATUS_EXTRACAO_INCOMPLETA,
            error_message=_short(f"IA não extraiu campos obrigatórios: {', '.join(exc.missing)}"),
        )
        summary.unprocessed += 1
        return
    except Exception as exc:  # falha operacional do Gemini — retentativa é a US 4.6
        _log(db, raw, STATUS_ERRO, error_message=_short(exc))
        summary.errors += 1
        return

    # US 4.4 / IESI-75: validação autónoma (estrutura + data futura) antes de
    # persistir — válida publica como "active", inválida é descartada com registo.
    payload = asdict(parsed)
    result = evaluate(payload)
    if result.decision is ValidationDecision.PUBLICAR:
        _persist(db, raw, parsed, summary, status="active", log_status=STATUS_PROCESSADO_IA)
        summary.processed_ia += 1
        return

    _log(
        db,
        raw,
        STATUS_EXTRACAO_INCOMPLETA,
        extracted_data=json.dumps(payload, default=str, ensure_ascii=False),
        error_message=_short(f"evento descartado pela validação: {', '.join(result.reason_texts)}"),
    )
    summary.discarded += 1


def _persist(
    db: Session,
    raw: RawEmail,
    parsed: ParsedEvent,
    summary: ExtractionSummary,
    *,
    status: str,
    log_status: str,
) -> None:
    event = Event(
        title=parsed.title,
        description=parsed.description or parsed.title,
        date=parsed.date,
        time=parsed.time,
        location=parsed.location,
        event_type=parsed.event_type,
        registration_link=parsed.registration_link,
        status=status,
        origin="email",
    )
    event = event_repository.create(db, event)
    _log(
        db,
        raw,
        log_status,
        extracted_data=json.dumps(asdict(parsed), default=str, ensure_ascii=False),
        event_id=event.id,
    )


def _log(
    db: Session,
    raw: RawEmail,
    status: str,
    *,
    extracted_data: str | None = None,
    error_message: str | None = None,
    event_id: int | None = None,
) -> None:
    extraction_log_repository.create(
        db,
        ExtractionLog(
            gmail_message_id=raw.message_id,
            source_email=raw.sender,
            status=status,
            extracted_data=extracted_data,
            error_message=error_message,
            event_id=event_id,
        ),
    )


def _short(exc: Exception) -> str:
    return str(exc)[:500]
