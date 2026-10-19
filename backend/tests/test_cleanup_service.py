"""Testes automatizados das User Stories US 5.1 e US 5.2 (Épico E5).

Cenários cobertos (Gherkin):
US 5.1:
- Cenário: Exclusão automática de evento expirado
  Dado que um evento tem data limite "2026-09-01"
  Quando a data atual é "2026-09-02"
  Então o evento é automaticamente removido da listagem
  E uma mensagem de log é registrada

- Cenário: Evento com data futura não é excluído
  Dado que um evento tem data limite "2026-10-01"
  Quando a data atual é "2026-09-05"
  Então o evento permanece visível na listagem

US 5.2:
- Cenário: Agendamento de limpeza
  Dado que o serviço de limpeza está configurado para rodar diariamente
  Quando a tarefa agendada é executada
  Então todos os eventos com data passada são excluídos
  E um relatório de limpeza é gerado
"""

import datetime as dt
import logging

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.main import app
from app.models.event import Event
from app.models.extraction_log import ExtractionLog
from app.repositories import event_repository
from app.services.events.cleanup_scheduler import (
    run_cleanup_job,
    shutdown_cleanup_scheduler,
    start_cleanup_scheduler,
)
from app.services.events.cleanup_service import (
    clean_expired_events,
    get_expired_events,
    is_event_expired,
)


def _criar_evento(
    db: Session,
    title: str,
    date: dt.date,
    time: dt.time = dt.time(10, 0),
    status: str = "active",
) -> Event:
    """Helper para persistir eventos de teste."""
    event = Event(
        title=title,
        description=f"Descrição de {title}",
        date=date,
        time=time,
        location="CIn - Auditório",
        event_type="Palestra",
        registration_link="https://cin.ufpe.br/inscricao",
        status=status,
        origin="manual",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


# ── US 5.1: Regra de Negócio de Expiração de Eventos ──────────────────


class TestExpiracaoEventosUS51:
    """Testes dos critérios de aceite da US 5.1."""

    def test_exclusao_automatica_de_evento_expirado_com_log(
        self, db_session: Session, caplog: pytest.LogCaptureFixture
    ):
        """Cenário Gherkin: Exclusão automática de evento expirado.

        Dado que um evento tem data limite "2026-09-01"
        Quando a data atual é "2026-09-02"
        Então o evento é automaticamente removido da listagem
        E uma mensagem de log é registrada.
        """
        # Dado que um evento tem data limite "2026-09-01"
        evento = _criar_evento(db_session, "Palestra de IA", dt.date(2026, 9, 1))
        evento_id = evento.id

        # Verifica que o evento inicialmente está na listagem
        assert any(e.id == evento_id for e in event_repository.get_all(db_session))

        # Quando a data atual é "2026-09-02"
        data_atual = dt.date(2026, 9, 2)
        with caplog.at_level(logging.INFO):
            report = clean_expired_events(db_session, reference_date=data_atual)

        # Então o evento é automaticamente removido da listagem
        eventos_ativos = event_repository.get_all(db_session)
        assert not any(e.id == evento_id for e in eventos_ativos)
        assert event_repository.get_by_id(db_session, evento_id) is None

        # E uma mensagem de log é registrada
        assert any(
            f"Evento expirado removido automaticamente: ID={evento_id}" in record.message
            for record in caplog.records
        )

        # E o relatório confirma a exclusão
        assert report.expired_count == 1
        assert evento_id in report.deleted_event_ids
        assert "Palestra de IA" in report.deleted_titles

    def test_evento_com_data_futura_nao_e_excluido(self, db_session: Session):
        """Cenário Gherkin: Evento com data futura não é excluído.

        Dado que um evento tem data limite "2026-10-01"
        Quando a data atual é "2026-09-05"
        Então o evento permanece visível na listagem.
        """
        # Dado que um evento tem data limite "2026-10-01"
        evento = _criar_evento(
            db_session, "Hackathon CIn 2026", dt.date(2026, 10, 1)
        )
        evento_id = evento.id

        # Quando a data atual é "2026-09-05"
        data_atual = dt.date(2026, 9, 5)
        report = clean_expired_events(db_session, reference_date=data_atual)

        # Então o evento permanece visível na listagem
        eventos_ativos = event_repository.get_all(db_session)
        assert any(e.id == evento_id for e in eventos_ativos)
        assert event_repository.get_by_id(db_session, evento_id) is not None

        # E nenhum evento foi marcado como expirado
        assert report.expired_count == 0
        assert report.deleted_event_ids == []

    def test_evento_no_proprio_dia_nao_e_expirado(self, db_session: Session):
        """Eventos marcados para o próprio dia de referência ainda estão válidos."""
        hoje = dt.date(2026, 9, 15)
        evento_hoje = _criar_evento(db_session, "Workshop Hoje", hoje)

        report = clean_expired_events(db_session, reference_date=hoje)

        assert report.expired_count == 0
        assert event_repository.get_by_id(db_session, evento_hoje.id) is not None

    def test_limpeza_multiplos_eventos_remove_apenas_expirados(
        self, db_session: Session
    ):
        """Testa cenário com múltiplos eventos mistos no passado e no futuro."""
        ref = dt.date(2026, 9, 10)

        ev_passado1 = _criar_evento(db_session, "Passado 1", dt.date(2026, 9, 1))
        ev_passado2 = _criar_evento(db_session, "Passado 2", dt.date(2026, 9, 9))
        ev_futuro1 = _criar_evento(db_session, "Futuro 1", dt.date(2026, 9, 11))
        ev_futuro2 = _criar_evento(db_session, "Futuro 2", dt.date(2026, 9, 20))

        report = clean_expired_events(db_session, reference_date=ref)

        assert report.expired_count == 2
        assert set(report.deleted_event_ids) == {ev_passado1.id, ev_passado2.id}

        # Futuros continuam ativos
        ativos = {e.id for e in event_repository.get_all(db_session)}
        assert ev_futuro1.id in ativos
        assert ev_futuro2.id in ativos
        assert ev_passado1.id not in ativos
        assert ev_passado2.id not in ativos

    def test_is_event_expired_helper(self):
        """Testa função auxiliar is_event_expired."""
        evento = Event(date=dt.date(2026, 9, 1))

        assert is_event_expired(evento, reference_date=dt.date(2026, 9, 2)) is True
        assert is_event_expired(evento, reference_date=dt.date(2026, 9, 1)) is False
        assert is_event_expired(evento, reference_date=dt.date(2026, 8, 31)) is False

    def test_desvinculacao_segura_com_log_de_extracao(self, db_session: Session):
        """Garante que evento criado por extração de e-mail é apagado desvinculando o log."""
        evento = _criar_evento(
            db_session, "Evento de E-mail", dt.date(2026, 8, 1)
        )
        log = ExtractionLog(
            gmail_message_id="msg_test_123",
            source_email="coord@cin.ufpe.br",
            status="processado",
            event_id=evento.id,
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)

        # Executa limpeza
        report = clean_expired_events(
            db_session, reference_date=dt.date(2026, 8, 2)
        )

        assert report.expired_count == 1
        assert event_repository.get_by_id(db_session, evento.id) is None

        # Log de extração deve permanecer no banco para auditoria com event_id nulo
        db_session.refresh(log)
        assert log.event_id is None
        assert log.status == "processado"


# ── US 5.2: Rotina Agendada (CRON) e Relatório ────────────────────────


class TestAgendamentoLimpezaUS52:
    """Testes dos critérios de aceite da US 5.2."""

    def test_execucao_autonoma_do_job_gera_relatorio(
        self, monkeypatch: pytest.MonkeyPatch, db_session: Session
    ):
        """Cenário Gherkin: Agendamento de limpeza.

        Dado que o serviço de limpeza está configurado para rodar diariamente
        Quando a tarefa agendada é executada
        Então todos os eventos com data passada são excluídos
        E um relatório de limpeza é gerado.
        """
        # Mocka SessionLocal para usar nossa sessão de teste em memória
        monkeypatch.setattr(
            "app.services.events.cleanup_scheduler.SessionLocal",
            lambda: db_session,
        )

        ontem = dt.date.today() - dt.timedelta(days=1)
        amanha = dt.date.today() + dt.timedelta(days=1)

        ev_ontem = _criar_evento(db_session, "Evento Ontem", ontem)
        ev_amanha = _criar_evento(db_session, "Evento Amanhã", amanha)

        # Quando a tarefa agendada é executada
        report = run_cleanup_job()

        # Então todos os eventos com data passada são excluídos
        assert report is not None
        assert report.expired_count == 1
        assert ev_ontem.id in report.deleted_event_ids
        assert event_repository.get_by_id(db_session, ev_ontem.id) is None

        # E o evento futuro permanece
        assert event_repository.get_by_id(db_session, ev_amanha.id) is not None

        # E um relatório de limpeza é gerado
        assert report.executed_at is not None
        assert report.reference_date == dt.date.today()
        assert "Limpeza concluída com sucesso" in report.message

    def test_start_and_shutdown_cleanup_scheduler(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        """Testa o ciclo de vida do scheduler (inicialização e encerramento)."""
        monkeypatch.setattr(
            "app.services.events.cleanup_scheduler.CLEANUP_ENABLED", True
        )
        monkeypatch.setattr(
            "app.services.events.cleanup_scheduler.CLEANUP_INTERVAL_MINUTES", 30
        )

        start_cleanup_scheduler()
        # Encerramento suave
        shutdown_cleanup_scheduler()

    def test_cleanup_scheduler_desativado_nao_inicia(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        """Quando CLEANUP_ENABLED=False, o agendador não deve criar jobs."""
        monkeypatch.setattr(
            "app.services.events.cleanup_scheduler.CLEANUP_ENABLED", False
        )
        start_cleanup_scheduler()
        shutdown_cleanup_scheduler()


# ── Rota da API: POST /events/cleanup ─────────────────────────────────


class TestEndpointCleanup:
    """Testes da rota HTTP POST /events/cleanup."""

    def test_trigger_cleanup_requer_autenticacao(self):
        """Tentativa sem JWT deve retornar 401 ou 403."""
        client = TestClient(app, raise_server_exceptions=False)
        response = client.post("/events/cleanup")
        assert response.status_code in (401, 403)

    def test_trigger_cleanup_com_sucesso(self, db_session: Session):
        """Admin autenticado pode disparar a limpeza e receber o relatório."""
        from app.database import get_db

        app.dependency_overrides[get_db] = lambda: db_session
        try:
            client = TestClient(app)

            # Gera token para admin
            token = create_access_token({"sub": "admin@cin.ufpe.br"})
            headers = {"Authorization": f"Bearer {token}"}

            # Cria evento expirado no banco
            _criar_evento(
                db_session, "Evento Passado API", dt.date(2026, 1, 10)
            )

            response = client.post(
                "/events/cleanup?reference_date=2026-01-15",
                headers=headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["expired_count"] >= 1
            assert "Evento Passado API" in data["deleted_titles"]
            assert "Limpeza concluída com sucesso" in data["message"]
        finally:
            app.dependency_overrides.pop(get_db, None)

