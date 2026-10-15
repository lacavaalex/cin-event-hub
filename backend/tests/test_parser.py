"""Testes do parser estruturado de e-mails (US 4.1).

Cobrem os cenários Gherkin do backlog v3:
- "Então o sistema extrai automaticamente: título, data, hora, local, tipo e descrição"
- "Então o e-mail é ignorado E um log de erro é registrado" (dados insuficientes)
"""

import datetime as dt

import pytest

from app.services.extracao_email.parser import (
    InsufficientDataError,
    parse_email,
)

EMAIL_VALIDO = """\
Prezados,

O Centro de Informática promove o Hackathon CIn 2025, aberto a todos os alunos.

Data: 25/11/2025
Hora: 14h
Local: Auditório do CIn

Inscrições pelo link: https://forms.example.com/hackathon-cin
"""


def test_extrai_todos_os_campos_obrigatorios():
    evento = parse_email("Convocação: Hackathon CIn 2025", EMAIL_VALIDO)

    assert evento.title == "Hackathon CIn 2025"
    assert evento.date == dt.date(2025, 11, 25)
    assert evento.time == dt.time(14, 0)
    assert evento.location == "Auditório do CIn"
    assert evento.event_type == "Hackathon"
    assert "Hackathon CIn 2025" in evento.description
    assert evento.registration_link == "https://forms.example.com/hackathon-cin"


def test_aceita_data_iso():
    body = "Data: 2025-11-30\nHora: 9:30\nLocal: Sala A"
    evento = parse_email("Palestra de IA", body)

    assert evento.date == dt.date(2025, 11, 30)
    assert evento.time == dt.time(9, 30)


def test_aceita_data_por_extenso():
    body = "Curso no dia 5 de dezembro de 2025, das 10h30 às 12h.\nLocal: Auditório CIn"
    evento = parse_email("Workshop de Python", body)

    assert evento.date == dt.date(2025, 12, 5)
    assert evento.time == dt.time(10, 30)


def test_infere_tipo_por_palavra_chave():
    for titulo, esperado in [
        ("Workshop de testes", "Workshop"),
        ("Hackathon 24h", "Hackathon"),
        ("Palestra sobre LLMs", "Palestra"),
        ("Cineclube do CIn", "Outro"),
    ]:
        evento = parse_email(titulo, "Data: 10/01/2026\nHora: 18h\nLocal: Auditório")
        assert evento.event_type == esperado, titulo


def test_email_sem_dados_obrigatorios_levanta_erro():
    with pytest.raises(InsufficientDataError) as exc:
        parse_email("Assunto avulso", "Apenas um texto de divulgação sem dados.")

    assert set(exc.value.missing) >= {"date", "time", "location"}


def test_email_sem_local_levanta_erro():
    body = "Data: 10/01/2026\nHora: 18h\nSem lugar informado."
    with pytest.raises(InsufficientDataError) as exc:
        parse_email("Palestra", body)

    assert "location" in exc.value.missing


def test_email_vazio_de_titulo_usa_primeira_linha_do_corpo():
    body = "Semana de Computação 2026\nData: 20/02/2026\nHora: 19h\nLocal: Auditório"
    evento = parse_email("", body)

    assert evento.title == "Semana de Computação 2026"