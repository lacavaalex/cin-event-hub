"""Schemas Pydantic da extração de e-mails (US 4.1)."""

from pydantic import BaseModel


class ExtractionRunResponse(BaseModel):
    """Resumo de um ciclo de extração retornado pelo endpoint."""

    fetched: int
    processed: int
    ignored: int
    errors: int
    duplicates: int
    message: str