"""Testes da camada de inspeção estrutural (US 4.4 / IESI-73).

Cobrem o critério "os campos obrigatórios não estão vazios" do Gherkin da
US 4.4 sobre o JSON devolvido pelo Gemini — sem banco e sem rede.
"""

import datetime as dt

from app.services.validacao import (
    REQUIRED_FIELDS,
    ValidationResult,
    ValidationReason,
    coerce_date,
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
