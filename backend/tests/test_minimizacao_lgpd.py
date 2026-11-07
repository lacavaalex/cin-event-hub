"""Testes da minimização de dados dos e-mails (LGPD) — IESI-60, US 4.1 a 4.6.

Usam a fixture ``db_session`` dos demais testes: rodam no banco que ela
entregar (SQLite em memória na develop; PostgreSQL com o schema oficial depois
da migração). Nada aqui depende de recurso específico de um dos dois.

Cobrem:
- unidade: domínio do remetente e máscara de e-mail/CPF/telefone (e o que NÃO
  pode ser mascarado: data, hora, intervalo de anos);
- integração: o que o serviço de extração realmente grava no banco, em cada
  caminho (parser, IA, descarte pela validação, erro, ignorado);
- varredura: nenhum texto do e-mail fora do evento (assinatura, remetente
  pessoal) aparece em NENHUMA coluna de texto/JSON de NENHUMA tabela.
"""

import datetime as dt

import pytest
from sqlalchemy import inspect, text

from app.models.event import Event
from app.models.extraction_log import ExtractionLog
from app.schemas.extracao import ExtractionAlertRead
from app.services.extracao_email.extraction_service import run_extraction
from app.services.extracao_email.gmail_client import RawEmail
from app.services.extracao_email.minimizacao import (
    DOMINIO_DESCONHECIDO,
    dominio_do_remetente,
    mascarar_dados_pessoais,
)
from app.services.extracao_email.parser import ParsedEvent
from app.services.ia_gemini.gemini_client import (
    GeminiExtractionError,
    UnprocessableEventError,
)

REMETENTE_PESSOAL = "Maria Souza <maria.souza.pessoal@cin.ufpe.br>"
EMAIL_PESSOAL = "maria.souza.pessoal@cin.ufpe.br"
GMAIL_PESSOAL = "maria.pessoal@gmail.com"
TELEFONE = "(81) 99999-8888"
CPF = "123.456.789-09"
SEGREDO = "SEGREDO-DA-ASSINATURA"

# Evento no 1º parágrafo; assinatura com dados pessoais depois.
EMAIL_COM_ASSINATURA = (
    "Palestra de Segurança 2030\n"
    "Data: 25/11/2030\n"
    "Hora: 14h\n"
    "Local: Auditório do CIn\n"
    "\n"
    "Atenciosamente,\n"
    f"Maria Souza - {GMAIL_PESSOAL} - {TELEFONE} - CPF {CPF}\n"
    f"{SEGREDO}\n"
)


class ClientFake:
    def __init__(self, emails):
        self._emails = list(emails)

    def is_configured(self):
        return True

    def fetch_new_emails(self):
        return list(self._emails)


class GeminiFake:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def is_configured(self):
        return True

    def extract_event(self, subject, body):
        if self.error:
            raise self.error
        return self.result


def _raw(message_id, body, subject="Convite: Evento de Teste", sender=REMETENTE_PESSOAL):
    return RawEmail(
        message_id=message_id,
        sender=sender,
        subject=subject,
        body=body,
        received_at=dt.datetime.now(dt.timezone.utc),
    )


# ── unidade: remetente ────────────────────────────────────────────────
@pytest.mark.parametrize(
    "remetente, esperado",
    [
        ("secretaria@cin.ufpe.br", "cin.ufpe.br"),
        (REMETENTE_PESSOAL, "cin.ufpe.br"),
        ('"Souza, Maria" <Maria@CIn.UFPE.br>', "cin.ufpe.br"),
        ("<maria@cin.ufpe.br>", "cin.ufpe.br"),
        ("sem endereço", DOMINIO_DESCONHECIDO),
        ("", DOMINIO_DESCONHECIDO),
        (None, DOMINIO_DESCONHECIDO),
        ("maria@", DOMINIO_DESCONHECIDO),
    ],
)
def test_dominio_do_remetente(remetente, esperado):
    assert dominio_do_remetente(remetente) == esperado


# ── unidade: máscaras ─────────────────────────────────────────────────
@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("fale com ana.lima+evento@gmail.com hoje", "fale com [e-mail] hoje"),
        ("CPF 123.456.789-09", "CPF [cpf]"),
        ("CPF 12345678909", "CPF [cpf]"),
        ("tel (81) 99999-8888", "tel [telefone]"),
        ("tel (81) 3333-4444", "tel [telefone]"),
        ("tel +55 81 99999-8888", "tel [telefone]"),
        ("tel 81 99999-8888", "tel [telefone]"),
        ("tel 99999-8888", "tel [telefone]"),
        ("a@b.com e c@d.org", "[e-mail] e [e-mail]"),
    ],
)
def test_mascara_dados_pessoais(entrada, esperado):
    assert mascarar_dados_pessoais(entrada) == esperado


@pytest.mark.parametrize(
    "texto",
    [
        "Data: 2030-11-25 às 14:00",
        "Semestre 2025-2026",
        "Dia 25/11/2030, 14h30",
        "Sala 2020, bloco A",
        "https://forms.example.com/hack?id=123",
        "Hackathon de 24 horas no CIn",
        "",
    ],
)
def test_mascara_nao_altera_dados_do_evento(texto):
    assert mascarar_dados_pessoais(texto) == texto


def test_mascara_aceita_none():
    assert mascarar_dados_pessoais(None) is None


# ── integração: o que o serviço grava ─────────────────────────────────
def test_log_guarda_so_o_dominio_do_remetente(db_session):
    run_extraction(db_session, ClientFake([_raw("m-1", EMAIL_COM_ASSINATURA)]))

    log = db_session.query(ExtractionLog).one()
    assert log.source_email == "cin.ufpe.br"
    assert EMAIL_PESSOAL not in log.source_email


def test_alerta_do_admin_nao_expoe_o_endereco_do_remetente(db_session):
    gemini = GeminiFake(error=UnprocessableEventError(["date"]))
    run_extraction(db_session, ClientFake([_raw("m-2", "texto livre sem data")]), gemini_client=gemini)

    log = db_session.query(ExtractionLog).one()
    alerta = ExtractionAlertRead.model_validate(log)
    assert alerta.source_email == "cin.ufpe.br"
    assert EMAIL_PESSOAL not in alerta.model_dump_json()


def test_extracted_data_do_log_sai_mascarado(db_session):
    # descartado pela validação (data no passado): o log é a única cópia do que a IA extraiu
    parsed = ParsedEvent(
        title="Hackathon CIn",
        date=dt.date(2020, 1, 1),
        time=dt.time(14, 0),
        location="Auditório do CIn",
        description=f"Contato: {GMAIL_PESSOAL}, {TELEFONE}, CPF {CPF}.",
        event_type="Hackathon",
        registration_link="https://forms.example.com/hack",
    )
    run_extraction(
        db_session,
        ClientFake([_raw("m-3", "email livre")]),
        gemini_client=GeminiFake(result=parsed),
    )

    log = db_session.query(ExtractionLog).one()
    assert log.status == "extracao_incompleta"
    dados = str(log.extracted_data)
    for pessoal in (GMAIL_PESSOAL, TELEFONE, CPF):
        assert pessoal not in dados
    assert "[e-mail]" in dados and "[telefone]" in dados and "[cpf]" in dados
    # os dados do evento continuam legíveis para a curadoria
    assert "Hackathon CIn" in dados and "2020-01-01" in dados


def test_error_message_nao_carrega_dados_pessoais(db_session):
    erro = GeminiExtractionError(
        f"resposta não é JSON válido: 'fale com {GMAIL_PESSOAL} ou {TELEFONE}'"
    )
    run_extraction(
        db_session,
        ClientFake([_raw("m-4", "email livre")]),
        gemini_client=GeminiFake(error=erro),
    )

    log = db_session.query(ExtractionLog).one()
    assert log.status == "erro"
    assert GMAIL_PESSOAL not in log.error_message
    assert TELEFONE not in log.error_message
    assert "[e-mail]" in log.error_message


def test_error_message_continua_cabendo_em_500_caracteres(db_session):
    erro = GeminiExtractionError(("x" * 480) + f" {GMAIL_PESSOAL}")
    run_extraction(
        db_session,
        ClientFake([_raw("m-5", "email livre")]),
        gemini_client=GeminiFake(error=erro),
    )

    mensagem = db_session.query(ExtractionLog).one().error_message
    assert len(mensagem) <= 500
    # cortar depois de mascarar: nenhum pedaço do endereço sobra
    assert "maria.pessoal" not in mensagem


def test_mensagem_de_erro_sem_dado_pessoal_nao_muda(db_session):
    # o ignorado da US 4.1 mantém o texto original (critério de aceite do Gherkin)
    run_extraction(db_session, ClientFake([_raw("m-6", "Apenas um aviso, sem dados de evento.")]))

    log = db_session.query(ExtractionLog).one()
    assert log.status == "ignorado"
    assert "dados obrigatórios" in log.error_message


# ── varredura: nada do e-mail fora do evento no banco inteiro ─────────
def _todos_os_textos_do_banco(db_session):
    """Conteúdo (como texto) de toda coluna de toda tabela do banco de teste."""
    insp = inspect(db_session.get_bind())
    textos = []
    for tabela in insp.get_table_names():
        for coluna in insp.get_columns(tabela):
            nome = coluna["name"]
            linhas = db_session.execute(
                text(f'SELECT CAST("{nome}" AS TEXT) FROM "{tabela}"')
            ).scalars()
            textos.extend(f"{tabela}.{nome}={valor}" for valor in linhas if valor)
    return textos


def test_assinatura_e_remetente_nao_aparecem_em_nenhuma_tabela(db_session):
    run_extraction(db_session, ClientFake([_raw("m-7", EMAIL_COM_ASSINATURA)]))

    assert db_session.query(Event).count() == 1  # o evento em si foi extraído
    tudo = "\n".join(_todos_os_textos_do_banco(db_session))
    assert "Palestra de Segurança 2030" in tudo  # dado pertinente é mantido
    for proibido in (EMAIL_PESSOAL, GMAIL_PESSOAL, TELEFONE, CPF, SEGREDO, "Maria Souza"):
        assert proibido not in tudo, f"'{proibido}' foi persistido"


def test_corpo_do_email_nao_vai_para_as_tabelas_extracao_e_email_associado(db_session):
    # No schema oficial (PostgreSQL) ``extracao`` tem input_text/prompt, que poderiam
    # guardar o corpo do e-mail; o backend não deve usá-las. Sem essas tabelas (SQLite
    # da develop, antes da migração) não há o que verificar.
    insp = inspect(db_session.get_bind())
    tabelas = [t for t in ("extracao", "email_associado") if insp.has_table(t)]
    if not tabelas:
        pytest.skip("tabelas extracao/email_associado só existem no schema PostgreSQL")

    run_extraction(db_session, ClientFake([_raw("m-8", EMAIL_COM_ASSINATURA)]))

    for tabela in tabelas:
        assert db_session.execute(text(f'SELECT count(*) FROM "{tabela}"')).scalar_one() == 0
