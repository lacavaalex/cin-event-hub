"""Testes do serviço de extração (US 4.1) sem rede.

Usa um cliente Gmail fake (duck-typed) para cobrir os fluxos do Gherkin:
- e-mail completo → evento persistido + log "processado"
- idempotência: o mesmo message_id não gera duplicata
- e-mail sem dados obrigatórios → log "ignorado" com erro registrado
- falha de rede/quota na Gmail API → resumo com mensagem, sem quebrar o job
"""

import datetime as dt

from app.models.event import Event
from app.models.extraction_log import ExtractionLog
from app.services.extracao_email.extraction_service import run_extraction
from app.services.extracao_email.gmail_client import RawEmail

EMAIL_OK = (
    "Palestra de Segurança 2026\n"
    "Data: 25/11/2025\n"
    "Hora: 14h\n"
    "Local: Auditório do CIn\n"
    "Mais detalhes na página do evento."
)
EMAIL_SEM_DADOS = "Apenas um aviso de manutenção no prédio, sem dados de evento."
EMAIL_SEM_LOCAL = "Data: 25/11/2025\nHora: 14h\nMas não informa onde será."


class ClientFake:
    """Cliente Gmail fake: não toca na rede nem em arquivos de credencial."""

    def __init__(self, emails, configured=True, fetch_error=None):
        self._emails = list(emails)
        self.configured = configured
        self.fetch_error = fetch_error

    def is_configured(self):
        return self.configured

    def fetch_new_emails(self):
        if self.fetch_error:
            raise self.fetch_error
        return list(self._emails)


def _raw(message_id, body, subject="Convite: Evento de Teste"):
    return RawEmail(
        message_id=message_id,
        sender="sec@cin.ufpe.br",
        subject=subject,
        body=body,
        received_at=dt.datetime.now(dt.timezone.utc),
    )


def test_email_completo_e_persistido_com_log(db_session):
    client = ClientFake([_raw("msg-1", EMAIL_OK, "Palestra de Segurança 2026")])

    summary = run_extraction(db_session, client)

    assert summary.fetched == 1
    assert summary.processed == 1
    assert summary.ignored == 0
    assert summary.errors == 0

    event = db_session.query(Event).one()
    assert event.title == "Palestra de Segurança 2026"
    assert event.date == dt.date(2025, 11, 25)
    assert event.time == dt.time(14, 0)
    assert event.location == "Auditório do CIn"
    assert event.origin == "email"
    assert event.status == "active"

    log = db_session.query(ExtractionLog).one()
    assert log.gmail_message_id == "msg-1"
    assert log.status == "processado"
    assert log.event_id == event.id
    assert log.error_message is None


def test_varredura_e_idempotente(db_session):
    raw = _raw("msg-dup", EMAIL_OK)
    client = ClientFake([raw])

    first = run_extraction(db_session, client)
    second = run_extraction(db_session, client)

    assert first.processed == 1
    assert second.duplicates == 1
    assert db_session.query(Event).count() == 1
    assert db_session.query(ExtractionLog).count() == 1


def test_email_sem_dados_e_ignorado_com_log_de_erro(db_session):
    client = ClientFake([_raw("msg-2", EMAIL_SEM_DADOS)])

    summary = run_extraction(db_session, client)

    assert summary.ignored == 1
    assert summary.processed == 0
    assert db_session.query(Event).count() == 0

    log = db_session.query(ExtractionLog).one()
    assert log.status == "ignorado"
    assert log.event_id is None
    assert "dados obrigatórios" in (log.error_message or "")


def test_email_sem_local_e_contado_como_ignorado(db_session):
    client = ClientFake([_raw("msg-3", EMAIL_SEM_LOCAL)])

    summary = run_extraction(db_session, client)

    assert summary.ignored == 1
    assert summary.processed == 0
    assert db_session.query(ExtractionLog).one().status == "ignorado"


def test_nao_configurado_nao_faz_nada(db_session):
    client = ClientFake([_raw("msg-4", EMAIL_OK)], configured=False)

    summary = run_extraction(db_session, client)

    assert summary.fetched == 0
    assert summary.message.startswith("extração não executada")
    assert db_session.query(Event).count() == 0


def test_falha_na_gmail_api_nao_quebra_o_job(db_session):
    client = ClientFake([], fetch_error=RuntimeError("quota exceed"))

    summary = run_extraction(db_session, client)

    assert summary.fetched == 0
    assert summary.processed == 0
    assert "falha ao buscar e-mails" in summary.message