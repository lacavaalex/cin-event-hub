"""Testes da paginação da listagem no repositório de eventos (IESI-71).

Rodam no PostgreSQL de testes (fixture ``db_session`` do conftest), então o
LIMIT/OFFSET é executado pelo mesmo banco da aplicação.
"""
import datetime as dt

from app.models.event import Event
from app.repositories import event_repository


def _titulos(eventos):
    return [e.title for e in eventos]


class TestGetAllPaginacao:
    def test_limit_restringe_a_quantidade_de_eventos(self, db_session, criar_eventos):
        criar_eventos(25)

        eventos = event_repository.get_all(db_session, limit=10, offset=0)

        assert len(eventos) == 10

    def test_sem_parametros_retorna_os_20_primeiros(self, db_session, criar_eventos):
        criar_eventos(25)

        eventos = event_repository.get_all(db_session)

        assert _titulos(eventos) == [f"Evento {i}" for i in range(1, 21)]

    def test_offset_pula_os_eventos_das_paginas_anteriores(self, db_session, criar_eventos):
        criar_eventos(25)

        eventos = event_repository.get_all(db_session, limit=10, offset=10)

        assert _titulos(eventos) == [f"Evento {i}" for i in range(11, 21)]

    def test_ultima_pagina_retorna_apenas_o_que_sobrou(self, db_session, criar_eventos):
        criar_eventos(25)

        eventos = event_repository.get_all(db_session, limit=10, offset=20)

        assert _titulos(eventos) == [f"Evento {i}" for i in range(21, 26)]

    def test_offset_alem_do_total_retorna_lista_vazia(self, db_session, criar_eventos):
        criar_eventos(5)

        assert event_repository.get_all(db_session, limit=10, offset=50) == []

    def test_so_eventos_ativos_entram_na_paginacao(self, db_session, criar_eventos):
        criar_eventos(3, status="active", prefixo="Ativo", data_inicial=dt.date(2030, 3, 1))
        criar_eventos(2, status="inactive", prefixo="Inativo")

        eventos = event_repository.get_all(db_session, limit=10, offset=0)

        assert _titulos(eventos) == ["Ativo 1", "Ativo 2", "Ativo 3"]

    def test_ordem_cronologica_considera_a_hora_no_mesmo_dia(self, db_session):
        for titulo, hora in [("Noite", dt.time(19, 0)), ("Manhã", dt.time(9, 0)), ("Tarde", dt.time(14, 0))]:
            db_session.add(
                Event(title=titulo, description="d", date=dt.date(2030, 1, 1), time=hora,
                      location="CIn", event_type="Outro",
                      registration_link="https://exemplo.com", status="active", origin="manual")
            )
        db_session.commit()

        eventos = event_repository.get_all(db_session, limit=2, offset=0)
        resto = event_repository.get_all(db_session, limit=2, offset=2)

        assert _titulos(eventos) == ["Manhã", "Tarde"]
        assert _titulos(resto) == ["Noite"]

    def test_paginas_nao_repetem_nem_perdem_eventos_empatados(self, db_session, criar_eventos):
        # 6 eventos na mesma data e hora: só o id desempata a ordem entre as páginas
        criar_eventos(6, dias_entre=0, prefixo="Mesmo horário")

        pagina_1 = event_repository.get_all(db_session, limit=3, offset=0)
        pagina_2 = event_repository.get_all(db_session, limit=3, offset=3)

        ids = [e.id for e in pagina_1 + pagina_2]
        assert len(ids) == 6
        assert len(set(ids)) == 6
