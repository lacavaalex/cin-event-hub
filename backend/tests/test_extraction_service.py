"""Testes do serviço de extração (US 4.1 + US 4.2 + US 4.4) sem rede.

Usa um cliente Gmail fake e um cliente Gemini fake (duck-typed) para cobrir os
fluxos do Gherkin das stories:

US 4.1
- e-mail completo → evento persistido + log "processado"
- idempotência: o mesmo message_id não gera duplicata
- e-mail sem dados obrigatórios → log "ignorado" com erro registrado
- falha de rede/quota na Gmail API → resumo com mensagem, sem quebrar o job

US 4.2
- parser estruturado falha, IA extrai → log "processado_ia"
- IA conclui que não é evento → "ignorado"
- IA confirma evento mas faltam campos → alerta ao admin
- falha operacional do Gemini → "erro"

US 4.4 (validação autónoma)
- IA extrai evento válido (data futura) → publicado com status "active"
- data no passado → evento descartado + log "extracao_incompleta"
- título vazio → evento descartado + log "extracao_incompleta"
- os descartes aparecem em GET /extraction/alerts (repositório)
"""

import datetime as dt

from app.models.event import Event
from app.models.extraction_log import ExtractionLog
from app.repositories import extraction_log_repository
from app.services.extracao_email.extraction_service import (
    STATUS_EXTRACAO_INCOMPLETA,
    STATUS_NAO_PROCESSADO,
    run_extraction,
)
from app.services.extracao_email.gmail_client import RawEmail
from app.services.extracao_email.parser import ParsedEvent
from app.services.ia_gemini.gemini_client import (
    GeminiExtractionError,
    NotAnEventError,
    UnprocessableEventError,
)
from app.services.validacao import LOCAL_TZ

EMAIL_OK = (
    "Palestra de Segurança 2026\n"
    "Data: 25/11/2025\n"
    "Hora: 14h\n"
    "Local: Auditório do CIn\n"
    "Mais detalhes na página do evento."
)
EMAIL_SEM_DADOS = "Apenas um aviso de manutenção no prédio, sem dados de evento."
EMAIL_SEM_LOCAL = "Data: 25/11/2025\nHora: 14h\nMas não informa onde será."

# Formatação variada: o parser estruturado não extrai data/hora → cai na IA.
EMAIL_LIVRE = (
    "Bora pro Hackathon CIn! Sexta que vem rola o Hackathon no auditório do CIn, "
    "começando à tarde. Vagas limitadas, não perca!"
)


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


# ── US 4.2: fallback de IA ────────────────────────────────────────────
class GeminiFake:
    """Cliente Gemini fake: devolve um resultado programado ou levanta um erro."""

    def __init__(self, result=None, error=None, configured=True):
        self.result = result
        self.error = error
        self.configured = configured
        self.calls = 0

    def is_configured(self):
        return self.configured

    def extract_event(self, subject, body):
        self.calls += 1
        if self.error:
            raise self.error
        return self.result


def _parsed_event(**overrides):
    base = dict(
        title="Hackathon CIn",
        date=dt.date(2027, 3, 20),
        time=dt.time(14, 0),
        location="Auditório do CIn",
        description="Hackathon de 24 horas no CIn.",
        event_type="Hackathon",
        registration_link="https://forms.example.com/hack",
    )
    base.update(overrides)
    return ParsedEvent(**base)


def test_ia_extrai_email_de_formato_variado_e_publica(db_session):
    client = ClientFake([_raw("ia-1", EMAIL_LIVRE, "Bora pro Hackathon CIn!")])
    gemini = GeminiFake(result=_parsed_event())

    summary = run_extraction(db_session, client, gemini_client=gemini)

    assert gemini.calls == 1
    assert summary.processed == 0
    assert summary.processed_ia == 1
    assert summary.discarded == 0

    event = db_session.query(Event).one()
    assert event.title == "Hackathon CIn"
    assert event.date == dt.date(2027, 3, 20)
    assert event.time == dt.time(14, 0)
    assert event.location == "Auditório do CIn"
    assert event.status == "active"   # US 4.4: validação aprovou → auto-publicado
    assert event.origin == "email"

    log = db_session.query(ExtractionLog).one()
    assert log.status == "processado_ia"
    assert log.event_id == event.id


def test_ia_conclui_que_nao_e_evento_e_ignora(db_session):
    client = ClientFake([_raw("ia-2", EMAIL_SEM_DADOS)])
    gemini = GeminiFake(error=NotAnEventError("não é evento"))

    summary = run_extraction(db_session, client, gemini_client=gemini)

    assert summary.ignored == 1
    assert summary.processed_ia == 0
    assert db_session.query(Event).count() == 0
    assert db_session.query(ExtractionLog).one().status == "ignorado"


def test_ia_sem_campos_obrigatorios_gera_alerta(db_session):
    client = ClientFake([_raw("ia-3", EMAIL_LIVRE, "Evento sem data")])
    gemini = GeminiFake(error=UnprocessableEventError(["date", "time"]))

    summary = run_extraction(db_session, client, gemini_client=gemini)

    assert summary.unprocessed == 1
    assert summary.processed_ia == 0
    assert db_session.query(Event).count() == 0

    log = db_session.query(ExtractionLog).one()
    # US 4.4: extração incompleta é registada para o dashboard e segue nos alertas.
    assert log.status == STATUS_EXTRACAO_INCOMPLETA
    assert "date" in (log.error_message or "")


def test_ia_com_falha_operacional_gera_erro(db_session):
    client = ClientFake([_raw("ia-4", EMAIL_LIVRE)])
    gemini = GeminiFake(error=GeminiExtractionError("timeout na API"))

    summary = run_extraction(db_session, client, gemini_client=gemini)

    assert summary.errors == 1
    assert summary.processed_ia == 0
    assert db_session.query(ExtractionLog).one().status == "erro"


# ── US 4.4: validação autónoma e auto-publicação ──────────────────────
def test_ia_com_data_no_passado_e_descartada(db_session):
    client = ClientFake([_raw("ia-5", EMAIL_LIVRE)])
    gemini = GeminiFake(result=_parsed_event(date=dt.date(2025, 1, 1)))

    summary = run_extraction(db_session, client, gemini_client=gemini)

    assert summary.processed_ia == 0
    assert summary.discarded == 1
    assert db_session.query(Event).count() == 0

    log = db_session.query(ExtractionLog).one()
    assert log.status == STATUS_EXTRACAO_INCOMPLETA
    assert log.event_id is None
    assert "data_no_passado" in (log.error_message or "")
    assert log.extracted_data is not None


def test_ia_com_titulo_vazio_e_descartada(db_session):
    client = ClientFake([_raw("ia-6", EMAIL_LIVRE)])
    gemini = GeminiFake(result=_parsed_event(title="   "))

    summary = run_extraction(db_session, client, gemini_client=gemini)

    assert summary.discarded == 1
    assert db_session.query(Event).count() == 0

    log = db_session.query(ExtractionLog).one()
    assert log.status == STATUS_EXTRACAO_INCOMPLETA
    assert "titulo_vazio" in (log.error_message or "")


def test_ia_com_data_de_hoje_e_publicada(db_session):
    client = ClientFake([_raw("ia-7", EMAIL_LIVRE)])
    hoje = dt.datetime.now(LOCAL_TZ).date()
    gemini = GeminiFake(result=_parsed_event(date=hoje))

    summary = run_extraction(db_session, client, gemini_client=gemini)

    assert summary.processed_ia == 1
    assert db_session.query(Event).one().status == "active"


def test_alertas_incluem_descartes_e_registos_legados(db_session):
    client = ClientFake([_raw("ia-8", EMAIL_LIVRE)])
    gemini = GeminiFake(result=_parsed_event(date=dt.date(2025, 1, 1)))
    run_extraction(db_session, client, gemini_client=gemini)

    db_session.add(
        ExtractionLog(
            gmail_message_id="legado-1",
            source_email="sec@cin.ufpe.br",
            status=STATUS_NAO_PROCESSADO,
            error_message="registo anterior à US 4.4",
        )
    )
    db_session.commit()

    alerts = extraction_log_repository.list_by_statuses(
        db_session,
        [STATUS_EXTRACAO_INCOMPLETA, STATUS_NAO_PROCESSADO],
    )

    assert {log.status for log in alerts} == {
        STATUS_EXTRACAO_INCOMPLETA,
        STATUS_NAO_PROCESSADO,
    }