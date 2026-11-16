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
