"""Validação autónoma da integridade estrutural dos dados extraídos pela IA.

Implementa a **US 4.4** do backlog v3 (Validação Autónoma) — etapa **IESI-73**:
uma camada de serviço que *inspeciona o JSON devolvido pelo Gemini* antes de
qualquer persistência, respondendo se a estrutura do evento está íntegra.

Regras estruturais (Gherkin da US 4.4: "os campos obrigatórios não estão vazios"):

- ``title`` presente e não vazio;
- ``date`` presente e conversível para :class:`datetime.date`.

A regra temporal ("a data é futura") e a decisão de publicar/descartar são a
etapa seguinte da US 4.4 (IESI-74). A camada é pura: não toca em banco nem em
rede — o pipeline de extração é quem persiste (IESI-75).
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping

# Campos cuja integridade a US 4.4 exige antes de publicar um evento extraído.
REQUIRED_FIELDS = ("title", "date")

# Formatos aceitos para a string de data vinda do JSON da IA.
_DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y")


class ValidationReason(StrEnum):
    """Motivo de rejeição da validação estrutural (IESI-73)."""

    TITULO_VAZIO = "titulo_vazio"
    DATA_VAZIA = "data_vazia"
    DATA_INVALIDA = "data_invalida"


@dataclass(frozen=True)
class ValidationResult:
    """Resultado da validação: sem motivos ⇒ válido."""

    reasons: tuple[ValidationReason, ...] = ()

    @property
    def valid(self) -> bool:
        return not self.reasons

    @property
    def status(self) -> str:
        """``"valido"`` / ``"invalido"`` — usado no registo do dashboard (IESI-75)."""
        return "valido" if self.valid else "invalido"

    @property
    def reason_texts(self) -> tuple[str, ...]:
        """Motivos como strings (prontas para ``error_message`` do log)."""
        return tuple(str(reason) for reason in self.reasons)


def inspect_payload(payload: Mapping[str, Any]) -> ValidationResult:
    """Inspeciona o JSON estruturado devolvido pelo Gemini (camada IESI-73).

    Aceita o dicionário da IA (ou ``dataclasses.asdict(parsed_event)``) e
    devolve os motivos de rejeição — vazio quando a estrutura está íntegra.
    """
    reasons: list[ValidationReason] = []

    if not _has_title(payload):
        reasons.append(ValidationReason.TITULO_VAZIO)

    raw_date = payload.get("date")
    if _is_blank(raw_date):
        reasons.append(ValidationReason.DATA_VAZIA)
    elif coerce_date(raw_date) is None:
        reasons.append(ValidationReason.DATA_INVALIDA)

    return ValidationResult(tuple(reasons))


def coerce_date(value: object) -> dt.date | None:
    """Converte o valor de ``date`` do JSON em :class:`datetime.date` (ou ``None``)."""
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        for fmt in _DATE_FORMATS:
            try:
                return dt.datetime.strptime(text, fmt).date()
            except ValueError:
                continue
    return None


def _has_title(payload: Mapping[str, Any]) -> bool:
    return not _is_blank(payload.get("title"))


def _is_blank(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    return False
