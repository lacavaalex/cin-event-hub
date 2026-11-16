"""Testes do cliente Gemini (US 4.2) sem chamar a API.

Substitui apenas ``_generate`` (a chamada de rede) por uma resposta programada,
exercitando toda a validação/parse do backend.
"""

import datetime as dt
import json

import pytest

from app.services.ia_gemini.gemini_client import (
    GeminiClient,
    GeminiExtractionError,
    NotAnEventError,
    UnprocessableEventError,
)


class FakeGemini(GeminiClient):
    """GeminiClient com a rede substituída por uma resposta fixa."""

    def __init__(self, response, **kwargs):
        kwargs.setdefault("api_key", "teste")
        super().__init__(**kwargs)
        self._response = response

    def _generate(self, prompt):
        if isinstance(self._response, Exception):
            raise self._response
        return self._response


def _json(**overrides):
    data = {
        "is_event": True,
        "title": "Workshop de Python",
        "date": "2026-03-12",
        "time": "09:30",
        "location": "Sala B-202",
        "event_type": "Workshop",
        "description": "Oficina prática de FastAPI.",
        "registration_link": "https://forms.example.com/workshop",
    }
    data.update(overrides)
    return json.dumps(data)


def test_is_configured_depende_da_chave():
    assert GeminiClient(api_key="abc").is_configured() is True
    assert GeminiClient(api_key="").is_configured() is False


def test_extrai_evento_valido():
    evento = FakeGemini(_json()).extract_event("Workshop", "corpo livre")

    assert evento.title == "Workshop de Python"
    assert evento.date == dt.date(2026, 3, 12)
    assert evento.time == dt.time(9, 30)
    assert evento.location == "Sala B-202"
    assert evento.event_type == "Workshop"
    assert evento.registration_link == "https://forms.example.com/workshop"


def test_aceita_resposta_entre_cercas_markdown():
    evento = FakeGemini(f"```json\n{_json()}\n```").extract_event("S", "b")
    assert evento.title == "Workshop de Python"


def test_aceita_data_brasileira_e_hora_com_h():
    evento = FakeGemini(_json(date="12/03/2026", time="9h")).extract_event("S", "b")
    assert evento.date == dt.date(2026, 3, 12)
    assert evento.time == dt.time(9, 0)


def test_tipo_invalido_vira_outro():
    evento = FakeGemini(_json(event_type="Show")).extract_event("S", "b")
    assert evento.event_type == "Outro"


def test_link_invalido_vira_vazio():
    evento = FakeGemini(_json(registration_link="sem link")).extract_event("S", "b")
    assert evento.registration_link == ""


def test_nao_e_evento_levanta_not_an_event():
    with pytest.raises(NotAnEventError):
        FakeGemini(_json(is_event=False)).extract_event("S", "b")


def test_sem_campos_obrigatorios_levanta_unprocessable():
    resposta = _json(date="", location="")
    with pytest.raises(UnprocessableEventError) as exc:
        FakeGemini(resposta).extract_event("S", "b")

    assert set(exc.value.missing) == {"date", "location"}


def test_data_invalida_conta_como_ausente():
    with pytest.raises(UnprocessableEventError) as exc:
        FakeGemini(_json(date="32/13/2026")).extract_event("S", "b")

    assert "date" in exc.value.missing


def test_json_invalido_levanta_erro_operacional():
    with pytest.raises(GeminiExtractionError):
        FakeGemini("isso não é json").extract_event("S", "b")


def test_falha_da_api_e_erro_operacional():
    with pytest.raises(GeminiExtractionError):
        FakeGemini(GeminiExtractionError("500")).extract_event("S", "b")


# ── Wiring do SDK real (google-genai), sem rede ──────────────────────
def test_generate_chama_sdk_e_retorna_texto(monkeypatch):
    genai = pytest.importorskip("google.genai")

    class _Response:
        text = _json()

    class _Models:
        def generate_content(self, **kwargs):
            return _Response()

    class _Client:
        def __init__(self, **kwargs):
            self.models = _Models()

    monkeypatch.setattr(genai, "Client", _Client)

    evento = GeminiClient(api_key="teste").extract_event("S", "b")
    assert evento.title == "Workshop de Python"


def test_generate_encapsula_erro_do_sdk(monkeypatch):
    genai = pytest.importorskip("google.genai")

    class _Models:
        def generate_content(self, **kwargs):
            raise RuntimeError("falha simulada")

    class _Client:
        def __init__(self, **kwargs):
            self.models = _Models()

    monkeypatch.setattr(genai, "Client", _Client)

    with pytest.raises(GeminiExtractionError):
        GeminiClient(api_key="teste")._generate("prompt")
