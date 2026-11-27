"""Testes do GET /events paginado (IESI-70), de ponta a ponta no PostgreSQL de testes.

Usa o TestClient do FastAPI (sem ``with``, então o lifespan — create_all,
seed de admin e scheduler — não roda) com a sessão do conftest no lugar de
``get_db``.
"""
import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def _titulos(resposta):
    return [e["title"] for e in resposta.json()["items"]]


class TestListarEventosPaginado:
    def test_sem_parametros_retorna_os_20_primeiros_com_metadados(self, client, criar_eventos):
        criar_eventos(45)

        resposta = client.get("/events")

        assert resposta.status_code == 200
        corpo = resposta.json()
        assert _titulos(resposta) == [f"Evento {i}" for i in range(1, 21)]
        assert corpo["page"] == 1
        assert corpo["total_pages"] == 3

    def test_pagina_seguinte_traz_os_proximos_eventos(self, client, criar_eventos):
        criar_eventos(45)

        resposta = client.get("/events", params={"page": 2})

        assert _titulos(resposta) == [f"Evento {i}" for i in range(21, 41)]
        assert resposta.json()["page"] == 2

    def test_ultima_pagina_traz_so_o_que_sobrou(self, client, criar_eventos):
        criar_eventos(45)

        resposta = client.get("/events", params={"page": 3})

        assert _titulos(resposta) == [f"Evento {i}" for i in range(41, 46)]
        corpo = resposta.json()
        assert corpo["page"] == corpo["total_pages"]  # não há próxima página

    def test_page_size_muda_o_tamanho_e_o_total_de_paginas(self, client, criar_eventos):
        criar_eventos(25)

        resposta = client.get("/events", params={"page_size": 10})

        assert len(resposta.json()["items"]) == 10
        assert resposta.json()["total_pages"] == 3

    def test_pagina_alem_do_total_devolve_lista_vazia(self, client, criar_eventos):
        criar_eventos(5)

        resposta = client.get("/events", params={"page": 9})

        assert resposta.status_code == 200
        corpo = resposta.json()
        assert corpo["items"] == []
        assert corpo["page"] == 9
        assert corpo["total_pages"] == 1

    def test_sem_eventos_devolve_zero_paginas(self, client):
        resposta = client.get("/events")

        assert resposta.status_code == 200
        assert resposta.json() == {"items": [], "page": 1, "total_pages": 0}

    def test_eventos_inativos_nao_entram_no_total(self, client, criar_eventos):
        criar_eventos(2, status="active", prefixo="Ativo")
        criar_eventos(30, status="inactive", prefixo="Inativo")

        corpo = client.get("/events").json()

        assert len(corpo["items"]) == 2
        assert corpo["total_pages"] == 1

    def test_cada_item_mantem_o_formato_do_evento(self, client, criar_eventos):
        criar_eventos(1)

        item = client.get("/events").json()["items"][0]

        assert set(item) == {
            "id", "title", "description", "date", "time", "location",
            "event_type", "registration_link", "status", "origin",
        }

    @pytest.mark.parametrize(
        "params",
        [{"page": 0}, {"page": -1}, {"page": "abc"}, {"page_size": 0}, {"page_size": 101}],
    )
    def test_parametros_invalidos_retornam_422(self, client, params):
        assert client.get("/events", params=params).status_code == 422
