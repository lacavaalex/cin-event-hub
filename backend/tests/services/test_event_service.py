"""Testes da paginação na camada de serviço de eventos (IESI-70).

O repositório é mockado (pytest-mock): aqui só se testa a regra do serviço —
cálculo do offset e do total de páginas.
"""
from unittest.mock import MagicMock

import pytest

from app.services import event_service


@pytest.fixture
def db():
    return MagicMock()


def _mock_repo(mocker, itens, total):
    get_all = mocker.patch("app.services.event_service.event_repository.get_all", return_value=itens)
    mocker.patch("app.services.event_service.event_repository.count_active", return_value=total)
    return get_all


class TestListEvents:
    def test_padrao_busca_a_primeira_pagina_de_20(self, db, mocker):
        get_all = _mock_repo(mocker, ["e"] * 20, total=45)

        pagina = event_service.list_events(db)

        get_all.assert_called_once_with(db, limit=20, offset=0)
        assert pagina.page == 1

    def test_offset_e_calculado_a_partir_da_pagina(self, db, mocker):
        get_all = _mock_repo(mocker, [], total=100)

        event_service.list_events(db, page=3, page_size=10)

        get_all.assert_called_once_with(db, limit=10, offset=20)

    @pytest.mark.parametrize(
        "total, page_size, esperado",
        [(0, 20, 0), (1, 20, 1), (20, 20, 1), (21, 20, 2), (45, 20, 3), (40, 20, 2), (7, 3, 3)],
    )
    def test_total_de_paginas_arredonda_para_cima(self, db, mocker, total, page_size, esperado):
        _mock_repo(mocker, [], total=total)

        pagina = event_service.list_events(db, page=1, page_size=page_size)

        assert pagina.total_pages == esperado

    def test_devolve_os_itens_do_repositorio(self, db, mocker):
        _mock_repo(mocker, ["a", "b"], total=2)

        pagina = event_service.list_events(db)

        assert pagina.items == ["a", "b"]
