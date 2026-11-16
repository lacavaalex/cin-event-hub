"""Validação autónoma da integridade estrutural e temporal dos dados da IA.

Implementa a **US 4.4** do backlog v3 (Validação Autónoma) em duas etapas:

- **IESI-73** — camada de serviço que *inspeciona o JSON devolvido pelo Gemini*
  antes de qualquer persistência (estrutura íntegra: ``title`` e ``date``
  presentes, não vazios e data conversível);
- **IESI-74** — regra de negócio: se **título ou data estiverem vazios**, ou se
  **a data extraída for no passado**, o evento é **descartado**; caso contrário
  a validação é ``"valido"`` e a decisão é ``"publicar"``.

Comparação de data usa o fuso de Recife (mesmo critério da US 2.1). A camada é
pura: não toca em banco nem em rede — o pipeline de extração é quem persiste
decisão a decisão (IESI-75).
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping
from zoneinfo import ZoneInfo

# Fuso horário local — o servidor pode rodar em UTC, mas a regra de data usa
# o horário de Recife (mesmo critério de event_service.create_event, US 2.1).
LOCAL_TZ = ZoneInfo("America/Recife")

# Campos cuja integridade a US 4.4 exige antes de publicar um evento extraído.
REQUIRED_FIELDS = ("title", "date")

# Formatos aceitos para a string de data vinda do JSON da IA.
_DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y")


class ValidationReason(StrEnum):
    """Motivos de rejeição da validação (IESI-73 + IESI-74)."""

    TITULO_VAZIO = "titulo_vazio"
    DATA_VAZIA = "data_vazia"
    DATA_INVALIDA = "data_invalida"
    DATA_NO_PASSADO = "data_no_passado"


class ValidationDecision(StrEnum):
    """Decisão resultante da validação autónoma (IESI-74)."""

    PUBLICAR = "publicar"
    DESCARTAR = "descartar"


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
    def decision(self) -> ValidationDecision:
        """``"publicar"`` se íntegro e com data não passada; senão ``"descartar"``."""
        return ValidationDecision.PUBLICAR if self.valid else ValidationDecision.DESCARTAR

    @property
    def reason_texts(self) -> tuple[str, ...]:
        """Motivos como strings (prontas para ``error_message`` do log)."""
        return tuple(str(reason) for reason in self.reasons)


def evaluate(
    payload: Mapping[str, Any], *, today: dt.date | None = None
) -> ValidationResult:
    """Validação completa da US 4.4: estrutura (IESI-73) + regra temporal (IESI-74).

    Regra da IESI-74: título ou data vazios, **ou** data extraída anterior à
    data atual ⇒ descarte. ``today`` permite fixar a data de referência em
    testes; por padrão usa o dia corrente em Recife.
    """
    result = inspect_payload(payload)
    if not result.valid:
        return result

    reference = today or dt.datetime.now(LOCAL_TZ).date()
    if coerce_date(payload.get("date")) < reference:
        return ValidationResult((ValidationReason.DATA_NO_PASSADO,))
    return result


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
