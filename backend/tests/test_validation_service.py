"""Testes da validação autónoma (US 4.4 — IESI-73 e IESI-74).

- IESI-73: inspeção estrutural do JSON devolvido pelo Gemini ("campos
  obrigatórios não estão vazios") — sem banco e sem rede.
- IESI-74: regra "título/data vazios ou data no passado ⇒ descartar"
  ("a data é futura" ⇒ publicar).
"""

import datetime as dt

from app.services.validacao import (
    REQUIRED_FIELDS,
    ValidationDecision,
    ValidationResult,
    ValidationReason,
    coerce_date,
    evaluate,
    inspect_payload,
)

PAYLOAD_COMPLETO = {
    "is_event": True,
    "title": "Palestra de IA",
    "date": "2027-03-20",
    "time": "14:00",
    "location": "Auditório do CIn",
    "event_type": "Palestra",
    "description": "Uma palestra sobre IA.",
    "registration_link": "https://forms.example.com/ia",
}


def test_payload_integro_e_valido():
    result = inspect_payload(PAYLOAD_COMPLETO)

    assert result.valid is True
    assert result.status == "valido"
    assert result.reasons == ()
    assert result.reason_texts == ()


def test_campos_obrigatorios_sao_titulo_e_data():
    assert REQUIRED_FIELDS == ("title", "date")
    assert ValidationResult().valid is True


def test_titulo_vazio_rejeita():
    result = inspect_payload({**PAYLOAD_COMPLETO, "title": "   "})

    assert result.valid is False
    assert result.status == "invalido"
    assert ValidationReason.TITULO_VAZIO in result.reasons


def test_titulo_ausente_rejeita():
    payload = {key: value for key, value in PAYLOAD_COMPLETO.items() if key != "title"}

    assert ValidationReason.TITULO_VAZIO in inspect_payload(payload).reasons


def test_data_vazia_ou_ausente_rejeita():
    assert ValidationReason.DATA_VAZIA in inspect_payload(
        {**PAYLOAD_COMPLETO, "date": None}
    ).reasons
    assert ValidationReason.DATA_VAZIA in inspect_payload(
        {**PAYLOAD_COMPLETO, "date": ""}
    ).reasons

    payload = {key: value for key, value in PAYLOAD_COMPLETO.items() if key != "date"}
    assert ValidationReason.DATA_VAZIA in inspect_payload(payload).reasons


def test_data_impossivel_rejeita():
    result = inspect_payload({**PAYLOAD_COMPLETO, "date": "31/02/2027"})

    assert result.valid is False
    assert ValidationReason.DATA_INVALIDA in result.reasons


def test_data_nao_string_rejeita():
    result = inspect_payload({**PAYLOAD_COMPLETO, "date": 20270320})

    assert ValidationReason.DATA_INVALIDA in result.reasons


def test_formatos_de_data_aceitos():
    assert inspect_payload({**PAYLOAD_COMPLETO, "date": "20/03/2027"}).valid is True
    assert inspect_payload({**PAYLOAD_COMPLETO, "date": "20-03-2027"}).valid is True
    assert inspect_payload({**PAYLOAD_COMPLETO, "date": "20.03.2027"}).valid is True
    assert inspect_payload(
        {**PAYLOAD_COMPLETO, "date": dt.date(2027, 3, 20)}
    ).valid is True


def test_titulo_e_data_invalidos_acumulam_motivos():
    result = inspect_payload({"title": "", "date": None})

    assert result.valid is False
    assert result.reasons == (
        ValidationReason.TITULO_VAZIO,
        ValidationReason.DATA_VAZIA,
    )
    assert result.reason_texts == ("titulo_vazio", "data_vazia")


def test_campos_extras_sao_ignorados():
    result = inspect_payload({**PAYLOAD_COMPLETO, "unknown_field": "?"})

    assert result.valid is True


def test_coerce_date():
    assert coerce_date("2027-03-20") == dt.date(2027, 3, 20)
    assert coerce_date("20/03/2027") == dt.date(2027, 3, 20)
    assert coerce_date(dt.date(2027, 3, 20)) == dt.date(2027, 3, 20)
    assert coerce_date(dt.datetime(2027, 3, 20, 10, 30)) == dt.date(2027, 3, 20)
    assert coerce_date("") is None
    assert coerce_date("amanhã") is None
    assert coerce_date(None) is None


# ── US 4.4 / IESI-74: regra temporal e decisão ────────────────────────
HOJE = dt.date(2026, 10, 19)


def test_data_no_passado_e_descartada():
    payload = {**PAYLOAD_COMPLETO, "date": "2025-11-25"}

    result = evaluate(payload, today=HOJE)

    assert result.valid is False
    assert result.status == "invalido"
    assert result.reasons == (ValidationReason.DATA_NO_PASSADO,)
    assert result.decision == ValidationDecision.DESCARTAR


def test_data_de_hoje_e_publicada():
    payload = {**PAYLOAD_COMPLETO, "date": "19/10/2026"}

    assert evaluate(payload, today=HOJE).decision == ValidationDecision.PUBLICAR


def test_data_futura_e_publicada():
    result = evaluate(PAYLOAD_COMPLETO, today=HOJE)

    assert result.valid is True
    assert result.status == "valido"
    assert result.decision == ValidationDecision.PUBLICAR


def test_titulo_ou_data_vazos_ja_sao_descartados():
    sem_titulo = evaluate({**PAYLOAD_COMPLETO, "title": " "}, today=HOJE)
    sem_data = evaluate({**PAYLOAD_COMPLETO, "date": None}, today=HOJE)

    assert sem_titulo.decision == ValidationDecision.DESCARTAR
    assert sem_data.decision == ValidationDecision.DESCARTAR


def test_estrutura_invalida_nao_acumula_motivo_temporal():
    payload = {"title": "Sem data", "date": None}

    result = evaluate(payload, today=HOJE)

    assert result.reasons == (ValidationReason.DATA_VAZIA,)
    assert result.decision == ValidationDecision.DESCARTAR


def test_data_no_passado_sobre_estrutura_valida_e_o_unico_motivo():
    payload = {**PAYLOAD_COMPLETO, "date": dt.date(2020, 1, 1)}

    result = evaluate(payload, today=HOJE)

    assert result.reasons == (ValidationReason.DATA_NO_PASSADO,)
    assert result.reason_texts == ("data_no_passado",)


def test_padrao_usa_data_atual_de_recife():
    payload = {**PAYLOAD_COMPLETO, "date": "2099-01-01"}

    assert evaluate(payload).valid is True


def test_decisao_publicar_quando_sem_motivos():
    assert ValidationResult().decision == ValidationDecision.PUBLICAR
