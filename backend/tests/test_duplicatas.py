"""Testes puros da comparação de títulos usada na desduplicação (US 4.5).

Não precisam de banco: cobrem a normalização e o limite de similaridade aplicados
pelo repositório de eventos (IESI-76).
"""

import pytest

from app.core.texto import (
    SIMILARIDADE_MINIMA,
    normalizar_titulo,
    titulos_sao_similares,
)


class TestNormalizarTitulo:
    @pytest.mark.parametrize(
        ("titulo", "esperado"),
        [
            ("Palestra de IA", "palestra de ia"),
            ("  palestra   DE   ia  ", "palestra de ia"),
            ("Seminário de Visão Computacional", "seminario de visao computacional"),
            ("Hackathon CIn!", "hackathon cin"),
            ("Oficina: Prompt Engineering?", "oficina prompt engineering"),
        ],
    )
    def test_remove_caixa_acentos_pontuacao_e_espacos(self, titulo, esperado):
        assert normalizar_titulo(titulo) == esperado

    @pytest.mark.parametrize(
        ("titulo", "esperado"),
        [
            ("Lembrete: Palestra de IA", "palestra de ia"),
            ("Palestra de IA (Lembrete)", "palestra de ia"),
            ("Relembrando - Hackathon CIn", "hackathon cin"),
            ("Aviso: Palestra de IA", "palestra de ia"),
        ],
    )
    def test_remove_marcador_de_lembrete_nas_bordas(self, titulo, esperado):
        assert normalizar_titulo(titulo) == esperado

    def test_nao_remove_palavra_do_meio_do_titulo(self):
        assert normalizar_titulo("Palestra sobre Aviso de Segurança") == (
            "palestra sobre aviso de seguranca"
        )

    def test_titulo_vazio(self):
        assert normalizar_titulo("   ") == ""


class TestTitulosSaoSimilares:
    @pytest.mark.parametrize(
        ("a", "b"),
        [
            ("Palestra de IA", "palestra de ia"),
            ("Seminário de Visão Computacional", "Seminario de Visao Computacional"),
            ("Lembrete: Palestra de IA", "Palestra de IA"),
            ("Palestra de IA", "Palestra de IA (lembrete)"),
            ("Hackathon CIn", "Hackathon do CIn"),
        ],
    )
    def test_titulos_iguais_ou_similares_sao_duplicatas(self, a, b):
        assert titulos_sao_similares(a, b) is True

    @pytest.mark.parametrize(
        ("a", "b"),
        [
            ("Palestra de IA", "Minicurso de SQL"),
            ("Hackathon CIn", "Semana da Computação"),
            ("Oficina de Prompt Engineering com Gemini", "Oficina de Prompt Engineering"),
        ],
    )
    def test_titulos_distintos_nao_sao_duplicatas(self, a, b):
        assert titulos_sao_similares(a, b) is False

    def test_limite_personalizado_pode_ser_mais_frouxo(self):
        a = "Oficina de Prompt Engineering com Gemini"
        b = "Oficina de Prompt Engineering"

        assert titulos_sao_similares(a, b, limite=SIMILARIDADE_MINIMA) is False
        assert titulos_sao_similares(a, b, limite=0.80) is True

    @pytest.mark.parametrize("a,b", [("", "Palestra de IA"), ("Palestra de IA", "")])
    def test_titulo_vazio_nunca_e_duplicata(self, a, b):
        assert titulos_sao_similares(a, b) is False
