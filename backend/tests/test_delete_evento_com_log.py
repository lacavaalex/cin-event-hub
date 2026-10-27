"""Apagar evento que veio de e-mail (US 2.3 e US 5.1) em PostgreSQL.

O SQLite não fiscalizava chaves estrangeiras; o PostgreSQL fiscaliza. O log de
extração aponta para o evento (``extraction_logs.event_id``) e precisa sobreviver
à exclusão dele, com ``event_id`` nulo.
"""
import datetime as dt

from app.models.event import Event
from app.models.extraction_log import ExtractionLog
from app.repositories.events import repository


def test_apagar_evento_extraido_de_email_mantem_o_log(db_session):
    evento = Event(
        title="Evento de e-mail", description="d", date=dt.date(2030, 1, 1),
        time=dt.time(10, 0), location="CIn", event_type="Outro",
        registration_link="", status="active", origin="email",
    )
    db_session.add(evento)
    db_session.commit()
    db_session.add(ExtractionLog(
        gmail_message_id="msg-1", source_email="sec@cin.ufpe.br",
        status="processado", event_id=evento.id,
    ))
    db_session.commit()

    repository.delete(db_session, evento)

    assert db_session.query(Event).count() == 0
    log = db_session.query(ExtractionLog).one()
    assert log.event_id is None
    assert log.status == "processado"
