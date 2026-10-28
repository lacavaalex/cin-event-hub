import datetime as dt

from pydantic import BaseModel, ConfigDict


class ExtractionRunResponse(BaseModel):
    fetched: int
    processed: int        # extraídos pelo parser estruturado (US 4.1)
    processed_ia: int     # extraídos pelo Gemini (US 4.2)
    ignored: int
    unprocessed: int      # eventos que a IA não completou (alerta ao admin)
    errors: int
    duplicates: int
    message: str


class ExtractionAlertRead(BaseModel):
    """Alerta de extração para o administrador (US 4.2).

    Cada item é um e-mail que a IA classificou como evento, mas cujos campos
    obrigatórios não puderam ser extraídos — fica registrado como "nao_processado".
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    gmail_message_id: str
    source_email: str
    status: str
    error_message: str | None
    created_at: dt.datetime
