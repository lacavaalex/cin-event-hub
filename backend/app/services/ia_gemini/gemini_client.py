from __future__ import annotations

import datetime as dt
import json
import re

from app.core.config import GEMINI_API_KEY, GEMINI_MAX_OUTPUT_TOKENS, GEMINI_MODEL
from app.services.extracao_email.parser import ParsedEvent

REQUIRED_FIELDS = ("title", "date", "time", "location")

_VALID_TYPES = ("Palestra", "Workshop", "Hackathon", "Outro")
_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.I | re.S)
_DESCRIPTION_MAX = 2000


class GeminiExtractionError(Exception):
    """Falha operacional do Gemini (API indisponível, JSON inválido, etc.)."""


class NotAnEventError(Exception):
    """O e-mail não divulga um evento (nada a cadastrar)."""


class UnprocessableEventError(Exception):
    """O e-mail é um evento, mas não foi possível extrair os campos obrigatórios."""

    def __init__(self, missing: list[str]) -> None:
        self.missing = list(missing)
        super().__init__(f"campos não extraídos: {', '.join(self.missing)}")


class GeminiClient:
    """Fachada sobre o Gemini: converte um e-mail em :class:`ParsedEvent`."""

    def __init__(
        self,
        api_key: str = GEMINI_API_KEY,
        model: str = GEMINI_MODEL,
        max_output_tokens: int = GEMINI_MAX_OUTPUT_TOKENS,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.max_output_tokens = max_output_tokens

    def is_configured(self) -> bool:
        """Indica se há chave do Gemini configurada no servidor."""
        return bool(self.api_key)

    # ── API pública ───────────────────────────────────────────────────
    def extract_event(self, subject: str, body: str) -> ParsedEvent:
        """Extrai o evento do e-mail via Gemini ou levanta uma das exceções."""
        from app.services.ia_gemini.prompt import build_prompt

        raw = self._generate(build_prompt(subject, body))
        data = self._parse_json(raw)

        if not data.get("is_event", False):
            raise NotAnEventError("e-mail não classificado como evento")

        return self._to_parsed_event(data)

    # ── internos ──────────────────────────────────────────────────────
    def _generate(self, prompt: str) -> str:
        """Chama o Gemini. Isolado para permitir substituição em testes."""
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:  # dependência só é necessária em produção
            raise GeminiExtractionError(
                "google-genai não instalado — pip install -r requirements.txt"
            ) from exc

        from app.services.ia_gemini.prompt import RESPONSE_SCHEMA, SYSTEM_INSTRUCTION

        try:
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                    max_output_tokens=self.max_output_tokens,
                    temperature=0.0,
                ),
            )
        except Exception as exc:  # rede/quota/modelo — tratado como falha operacional
            raise GeminiExtractionError(str(exc)) from exc
        return (response.text or "").strip()

    @staticmethod
    def _parse_json(raw: str) -> dict:
        cleaned = _FENCE.sub("", raw.strip()).strip()
        try:
            data = json.loads(cleaned)
        except (json.JSONDecodeError, ValueError) as exc:
            raise GeminiExtractionError(f"resposta não é JSON válido: {cleaned[:200]!r}") from exc
        if not isinstance(data, dict):
            raise GeminiExtractionError("resposta JSON não é um objeto")
        return data

    @staticmethod
    def _to_parsed_event(data: dict) -> ParsedEvent:
        date = GeminiClient._parse_date(data.get("date"))
        time_ = GeminiClient._parse_time(data.get("time"))
        title = str(data.get("title") or "").strip()
        location = str(data.get("location") or "").strip()

        values = {"title": title, "date": date, "time": time_, "location": location}
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise UnprocessableEventError(missing)

        event_type = str(data.get("event_type") or "Outro").strip()
        if event_type not in _VALID_TYPES:
            event_type = "Outro"

        link = str(data.get("registration_link") or "").strip()
        if not link.lower().startswith(("http://", "https://")):
            link = ""

        description = str(data.get("description") or "").strip() or title
        if len(description) > _DESCRIPTION_MAX:
            description = description[:_DESCRIPTION_MAX].rstrip() + "…"

        return ParsedEvent(
            title=title,
            date=date,
            time=time_,
            location=location,
            description=description,
            event_type=event_type,
            registration_link=link,
        )

    @staticmethod
    def _parse_date(value: object) -> dt.date | None:
        if not value:
            return None
        text = str(value).strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
            try:
                return dt.datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _parse_time(value: object) -> dt.time | None:
        if not value:
            return None
        text = str(value).strip().lower().replace("h", ":")
        if text.endswith(":"):
            text += "00"
        match = re.match(r"^(\d{1,2}):(\d{2})", text)
        if not match:
            return None
        try:
            return dt.time(int(match.group(1)), int(match.group(2)))
        except ValueError:
            return None
