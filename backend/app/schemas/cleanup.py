"""Schemas para a rotina de expiração e limpeza de eventos (US 5.1 / 5.2)."""

import datetime as dt

from pydantic import BaseModel, ConfigDict


class CleanupReportSchema(BaseModel):
    """Schema do relatório de execução da limpeza de eventos expirados."""

    model_config = ConfigDict(from_attributes=True)

    executed_at: dt.datetime
    reference_date: dt.date
    expired_count: int
    deleted_event_ids: list[int]
    deleted_titles: list[str]
    message: str
