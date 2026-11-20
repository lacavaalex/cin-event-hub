import datetime as dt

from pydantic import BaseModel, ConfigDict


class ExtractionRunResponse(BaseModel):
    fetched: int
    processed: int        # extraídos pelo parser estruturado (US 4.1)
    processed_ia: int     # extraídos pelo Gemini e publicados (US 4.2 + 4.4)
    ignored: int
    unprocessed: int      # IA não extraiu campos obrigatórios (alerta ao admin)
    discarded: int        # validação autónoma descartou o evento (US 4.4)
    errors: int
    duplicates: int
    message: str


class ExtractionAlertRead(BaseModel):
    """Alerta de extração para o administrador (US 4.2 + US 4.4).

    Cada item é um e-mail que a IA classificou como evento, mas que não pôde ser
    publicado: campos obrigatórios não extraídos ou evento recusado pela
    validação autónoma (título/data vazios ou data no passado). Fica registrado
    como "extracao_incompleta" — e "nao_processado" para registos legados.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    gmail_message_id: str
    source_email: str
    status: str
    error_message: str | None
    created_at: dt.datetime


class ExtractionLogItem(BaseModel):
    """Item minimizado de log exibido no painel de status (US 4.3, LGPD)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    gmail_message_id: str
    source_email: str
    status: str
    error_message: str | None
    event_id: int | None
    created_at: dt.datetime


class ExtractionStatusResponse(BaseModel):
    """Resumo operacional da extração de e-mails (US 4.3 / BE-160)."""

    total_logs: int
    total_processed: int
    counts_by_status: dict[str, int]
    last_run_at: dt.datetime | None
    last_run_failed: bool
    last_error: str | None
    recent_processed: list[ExtractionLogItem]
    recent_errors: list[ExtractionLogItem]
