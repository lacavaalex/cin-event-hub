"""Model ORM do log de extração de e-mails (tabela 'extraction_logs').

Entidade "LogDeExtração":
id, e-mail de origem, status (processado/ignorado/erro), timestamp, dados extraídos.

Minimização de dados: o corpo do e-mail não é persistido — apenas
os campos já extraídos do evento e o identificador da mensagem, para idempotência
da varredura.
"""

import datetime as dt
from typing import Any

from sqlalchemy import DateTime, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ExtractionLog(Base):
    __tablename__ = "extraction_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    gmail_message_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    source_email: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20))  # processado | ignorado | erro
    extracted_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # SET NULL: o log é histórico da extração e sobrevive à exclusão do evento
    # (US 2.3 / US 5.1). Sem isso o PostgreSQL recusa apagar evento vindo de e-mail.
    event_id: Mapped[int | None] = mapped_column(
        ForeignKey("events.id_event", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
