"""Minimização de dados pessoais dos e-mails (LGPD) — IESI-60 (US 4.1 a 4.6).

Regra do DoD D8: nenhum dado pessoal irrelevante é persistido; os e-mails
processados só contribuem com dados pertinentes aos eventos.

O que este módulo garante, no ponto único em que o serviço de extração grava o
log (``extraction_service._log``):

* ``source_email`` guarda só o **domínio** do remetente (``cin.ufpe.br``), nunca
  o endereço pessoal. O administrador ainda enxerga de qual origem veio o e-mail.
* ``extracted_data`` e ``error_message`` têm **e-mails, CPFs e telefones
  mascarados** (``[e-mail]``, ``[cpf]``, ``[telefone]``). Mensagens de erro de
  bibliotecas externas (ex.: resposta do Gemini) podem ecoar trechos do e-mail.

Não faz parte deste módulo: o evento publicado (``events``), que é o dado
pertinente ao evento, e o texto enviado ao Gemini.
"""

from __future__ import annotations

import re
from email.utils import parseaddr

DOMINIO_DESCONHECIDO = "desconhecido"

MASCARA_EMAIL = "[e-mail]"
MASCARA_CPF = "[cpf]"
MASCARA_TELEFONE = "[telefone]"

_EMAIL = re.compile(r"[\w.+\-]+@[\w\-]+(?:\.[\w\-]+)+")
# CPF com ou sem pontuação (11 dígitos). Roda antes do telefone para que
# 11 dígitos seguidos virem [cpf] e não sejam lidos como celular.
_CPF = re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)")
# Telefone BR: só formatos que não se confundem com data, hora ou intervalo de
# anos ("2025-2026"): (DDD) + número, +55 + DDD + número ou celular com 9.
_TELEFONE = re.compile(
    r"(?:\+55[\s.\-]?)?\(\d{2}\)[\s.\-]?\d{4,5}[\s.\-]?\d{4}(?!\d)"
    r"|\+55[\s.\-]?\d{2}[\s.\-]?9?\d{4}[\s.\-]?\d{4}(?!\d)"
    r"|(?<![\d\-])(?:\d{2}[\s.\-])?9\d{4}[\s.\-]?\d{4}(?!\d)"
)


def dominio_do_remetente(remetente: str | None) -> str:
    """Reduz ``"Maria <maria@cin.ufpe.br>"`` ao domínio ``"cin.ufpe.br"``.

    Sem endereço válido, devolve ``"desconhecido"`` (a coluna é NOT NULL).
    """
    _, endereco = parseaddr(remetente or "")
    if "@" not in endereco:
        return DOMINIO_DESCONHECIDO
    dominio = endereco.rsplit("@", 1)[1].strip().strip(">").lower()
    return dominio or DOMINIO_DESCONHECIDO


def mascarar_dados_pessoais(texto: str | None) -> str | None:
    """Troca e-mails, CPFs e telefones do texto por máscaras. ``None`` passa direto."""
    if texto is None:
        return None
    texto = _EMAIL.sub(MASCARA_EMAIL, texto)
    texto = _CPF.sub(MASCARA_CPF, texto)
    return _TELEFONE.sub(MASCARA_TELEFONE, texto)
