"""Cliente de leitura da caixa institucional via Gmail API + OAuth 2.0.

Obackend autentica-se com OAuth 2.0 para varrer a
caixa do e-mail institucional. As chaves/credenciais ficam apenas no servidor. Os imports das bibliotecas do Google são feitos dentro dos métodos
para que o restante do serviço (parser, scheduler, testes) funcione mesmo sem
elas instaladas, e para que a aplicação leve exatamente as dependências que usa.

Autorização inicial (uma única vez, em máquina com navegador):
    1. Baixe o arquivo client_secret no console do GCP no formato "Desktop app"
       e salve em GMAIL_CREDENTIALS_FILE.
    2. Rode o endpoint POST /extraction/run (ou o script) — o navegador abre o
       consentimento e o token é salvo em GMAIL_TOKEN_FILE com refresh.
"""

from __future__ import annotations

import datetime as dt
import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.config import (
    GMAIL_CREDENTIALS_FILE,
    GMAIL_MAX_RESULTS,
    GMAIL_QUERY,
    GMAIL_TOKEN_FILE,
)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


@dataclass(frozen=True)
class RawEmail:
    """E-mail recebido — contém apenas metadados e texto do evento (LGPD)."""

    message_id: str
    sender: str
    subject: str
    body: str
    received_at: dt.datetime | None = None


class GmailClient:
    """Fachada sobre a Gmail API: busca mensagens e normaliza o corpo em texto."""

    def __init__(
        self,
        credentials_file: str = GMAIL_CREDENTIALS_FILE,
        token_file: str = GMAIL_TOKEN_FILE,
        query: str = GMAIL_QUERY,
        max_results: int = GMAIL_MAX_RESULTS,
    ) -> None:
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.query = query
        self.max_results = max_results

    def is_configured(self) -> bool:
        """Indica se credenciais/token estão disponíveis no servidor."""
        return Path(self.credentials_file).exists() and Path(self.token_file).exists()

    def fetch_new_emails(self) -> list[RawEmail]:
        """Busca as mensagens mais recentes que casam com a query configurada."""
        service = self._service()
        result = (
            service.users()
            .messages()
            .list(userId="me", q=self.query, maxResults=self.max_results)
            .execute()
        )
        emails: list[RawEmail] = []
        for msg in result.get("messages", []):
            full = (
                service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="full")
                .execute()
            )
            parsed = self._to_raw_email(full)
            if parsed is not None:
                emails.append(parsed)
        return emails

    # ── internos ──────────────────────────────────────────────────────
    def _service(self) -> Any:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        creds = None
        if Path(self.token_file).exists():
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        if creds is not None and creds.valid:
            pass
        elif creds is not None and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not Path(self.credentials_file).exists():
                raise FileNotFoundError(
                    f"Credenciais OAuth não encontradas em {self.credentials_file}. "
                    "Configure GMAIL_CREDENTIALS_FILE (client_secret do GCP)."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, SCOPES
            )
            creds = flow.run_local_server(port=0)
        Path(self.token_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.token_file, "w", encoding="utf-8") as fh:
            fh.write(creds.to_json())
        return build("gmail", "v1", credentials=creds)

    @staticmethod
    def _to_raw_email(msg: dict[str, Any]) -> RawEmail | None:
        payload = msg.get("payload") or {}
        headers = {h["name"].lower(): h["value"] for h in (payload.get("headers") or [])}
        subject = headers.get("subject", "").strip()
        sender = headers.get("from", "").strip()
        body = GmailClient._extract_body(payload)

        internal_date = msg.get("internalDate")
        received_at = None
        if internal_date:
            try:
                received_at = dt.datetime.fromtimestamp(
                    int(internal_date) / 1000, tz=dt.timezone.utc
                )
            except (ValueError, OSError, OverflowError):
                received_at = None

        if not body and not subject:
            return None
        return RawEmail(
            message_id=msg.get("id", ""),
            sender=sender,
            subject=subject,
            body=body,
            received_at=received_at,
        )

    @staticmethod
    def _extract_body(payload: dict[str, Any]) -> str:
        """Coleta o texto da mensagem (text/plain de preferência; fallback HTML)."""
        parts = payload.get("parts") or []
        if not parts:
            return GmailClient._part_to_text(payload)

        plain = [p for p in parts if (p.get("mimeType") == "text/plain")]
        source = plain[0] if plain else parts[0]
        return GmailClient._part_to_text(source)

    @staticmethod
    def _part_to_text(part: dict[str, Any]) -> str:
        import base64

        mime = part.get("mimeType", "")
        data = part.get("body", {}).get("data", "")
        if not data:
            return ""
        try:
            decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        except Exception:
            return ""
        if mime == "text/html":
            return GmailClient._html_to_text(decoded)
        return decoded

    @staticmethod
    def _html_to_text(html_source: str) -> str:
        from html import unescape

        text = re.sub(r"<(br|/p|/div|/li|/tr)\s*/?>", "\n", html_source, flags=re.I)
        text = re.sub(r"<script.*?</script>", " ", text, flags=re.I | re.S)
        text = re.sub(r"<style.*?</style>", " ", text, flags=re.I | re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        return unescape(re.sub(r"[ \t]+", " ", text))