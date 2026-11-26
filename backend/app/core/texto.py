"""Comparação de títulos para detecção de lembretes/duplicatas (US 4.5).

A regra precisa ser pura (sem banco, rede ou framework) para que a camada de
aplicação possa reutilizá-la tanto no parser estruturado (US 4.1) quanto no
fallback de IA (US 4.2). O repositório de eventos usa estas funções para
selecionar os candidatos ativos da mesma data; a decisão final de duplicata
depende também da igualdade de data, feita no SQL.

Normalização
------------
* caixa, acentos e pontuação são ignorados ("Seminário" == "seminario");
* espaços repetidos viram um único espaço;
* marcadores de lembrete no início/fim ("Lembrete:", "(Relembrando)") são
  removidos — é exatamente o caso da US 4.5;
* títulos restantes são comparados por igualdade exata ou por similaridade
  ``SequenceMatcher`` com limite padrão 0,85 (aceita pequenas variações como
  "Hackathon CIn" × "Hackathon do CIn", mas não títulos distintos).

Não é usado ``pg_trgm``: a extensão não faz parte do schema oficial e a consulta
do repositório já é estreita (eventos ativos de uma única data).
"""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher

SIMILARIDADE_MINIMA = 0.85

_NAO_ALFANUMERICO = re.compile(r"[^\w\s]+", re.UNICODE)
_MARCADORES_LEMBRETE = frozenset(
    {
        "aviso",
        "lembrete",
        "relembrando",
        "recordacao",
        "recordatorio",
        "reminder",
    }
)


def normalizar_titulo(titulo: str) -> str:
    """Devolve o título em forma comparável: sem acento, caixa ou pontuação."""
    sem_acentos = unicodedata.normalize("NFKD", titulo or "")
    sem_acentos = "".join(
        caractere
        for caractere in sem_acentos
        if not unicodedata.combining(caractere)
    )
    sem_pontuacao = _NAO_ALFANUMERICO.sub(" ", sem_acentos.casefold())
    palavras = sem_pontuacao.split()

    while palavras and palavras[0] in _MARCADORES_LEMBRETE:
        palavras.pop(0)
    while palavras and palavras[-1] in _MARCADORES_LEMBRETE:
        palavras.pop()

    return " ".join(palavras)


def titulos_sao_similares(
    titulo_a: str,
    titulo_b: str,
    *,
    limite: float = SIMILARIDADE_MINIMA,
) -> bool:
    """Verdadeiro se os títulos forem iguais após normalização ou similares.

    ``limite`` permite ajustar o rigor da comparação em testes; o valor padrão
    é o critério adotado pela US 4.5 para "mesmo título (ou similar)".
    """
    a = normalizar_titulo(titulo_a)
    b = normalizar_titulo(titulo_b)
    if not a or not b:
        return False
    if a == b:
        return True
    return SequenceMatcher(None, a, b, autojunk=False).ratio() >= limite
