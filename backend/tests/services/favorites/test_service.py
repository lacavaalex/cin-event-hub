"""Testes da camada de serviço de favoritos (US 6.1).

Cada teste espelha um cenário em Gherkin do critério de aceite. Nenhum
teste aqui toca um banco de verdade: os repositórios (events e favorites)
são mockados via pytest-mock (fixture `mocker`).

Requer `pytest-mock` no requirements.txt / requirements-dev.txt.
"""
from unittest.mock import MagicMock

import pytest

from app.services.favorites import service


@pytest.fixture
def db():
    """Sessão falsa: o service só repassa `db` adiante — quem usaria a
    sessão de verdade (o repositório) está mockado em cada teste."""
    return MagicMock()


class TestFavoriteEvent:
    def test_favoritar_evento_existente_ainda_nao_favoritado(self, db, mocker):
        """
        Dado um evento existente que o usuário ainda não favoritou
        Quando ele favorita o evento
        Então um novo favorito é criado
        E o retorno indica is_favorited=True
        """
        mocker.patch(
            "app.services.favorites.service.events_repository.get_by_id",
            return_value=MagicMock(id=1),
        )
        mocker.patch(
            "app.services.favorites.service.favorites_repository.get",
            return_value=None,
        )
        create_mock = mocker.patch(
            "app.services.favorites.service.favorites_repository.create"
        )

        result = service.favorite_event(db, user_id=10, event_id=1)

        create_mock.assert_called_once_with(db, 10, 1)
        assert result.event_id == 1
        assert result.is_favorited is True

    def test_favoritar_evento_ja_favoritado_e_idempotente(self, db, mocker):
        """
        Dado um evento que o usuário já tinha favoritado
        Quando ele favorita novamente
        Então nenhum favorito duplicado é criado
        E o retorno ainda indica is_favorited=True
        """
        mocker.patch(
            "app.services.favorites.service.events_repository.get_by_id",
            return_value=MagicMock(id=1),
        )
        mocker.patch(
            "app.services.favorites.service.favorites_repository.get",
            return_value=MagicMock(),  # já existe um favorito
        )
        create_mock = mocker.patch(
            "app.services.favorites.service.favorites_repository.create"
        )

        result = service.favorite_event(db, user_id=10, event_id=1)

        create_mock.assert_not_called()
        assert result.is_favorited is True

    def test_favoritar_evento_inexistente_levanta_erro(self, db, mocker):
        """
        Dado que o evento não existe
        Quando o usuário tenta favoritá-lo
        Então EventNotFoundError é levantado
        E nenhum favorito é criado
        """
        mocker.patch(
            "app.services.favorites.service.events_repository.get_by_id",
            return_value=None,
        )
        create_mock = mocker.patch(
            "app.services.favorites.service.favorites_repository.create"
        )

        with pytest.raises(service.EventNotFoundError):
            service.favorite_event(db, user_id=10, event_id=999)

        create_mock.assert_not_called()


class TestUnfavoriteEvent:
    def test_desfavoritar_evento_favoritado(self, db, mocker):
        """
        Dado um evento favoritado pelo usuário
        Quando ele desfavorita o evento
        Então o favorito é removido
        E o retorno indica is_favorited=False
        """
        existing = MagicMock()
        mocker.patch(
            "app.services.favorites.service.favorites_repository.get",
            return_value=existing,
        )
        delete_mock = mocker.patch(
            "app.services.favorites.service.favorites_repository.delete"
        )

        result = service.unfavorite_event(db, user_id=10, event_id=1)

        delete_mock.assert_called_once_with(db, existing)
        assert result.is_favorited is False

    def test_desfavoritar_evento_nao_favoritado_e_idempotente(self, db, mocker):
        """
        Dado um evento que o usuário não tinha favoritado
        Quando ele tenta desfavoritar mesmo assim
        Então nada é removido e nenhum erro é levantado
        E o retorno indica is_favorited=False
        """
        mocker.patch(
            "app.services.favorites.service.favorites_repository.get",
            return_value=None,
        )
        delete_mock = mocker.patch(
            "app.services.favorites.service.favorites_repository.delete"
        )

        result = service.unfavorite_event(db, user_id=10, event_id=1)

        delete_mock.assert_not_called()
        assert result.is_favorited is False