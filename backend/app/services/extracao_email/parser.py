"""Parser estruturado de e-mails de eventos.

Extrai título, data, hora, local, tipo e descrição de e-mails institucionais
através de heurísticas de formatação comum: campos rotulados (Local:, Data: ...),
padrões de data/hora e palavras-chave de tipo. Não usa IA de propósito — o
processamento de formatação variada com Gemini é a User Story 4.2.

Campos obrigatórios: título, data, hora e local. Se algum faltar, ``parse_email``
levanta :class:`InsufficientDataError` e o serviço registra o e-mail como "ignorado"
(critério de aceite: e-mail sem dados suficientes é ignorado + log de erro).
"""

import datetime as dt
import html
import re
from dataclasses import dataclass, field

# Campos sem os quais um evento não pode ser cadastrado (Gherkin da US 4.1).
REQUIRED_FIELDS = ("title", "date", "time", "location")

_LOCATION_LABELED = re.compile(
    r"(?im)^\s*(?:local|onde|localiza[çc][aã]o|localizacao|endere[çc]o|address)\s*[:\-–]\s*(.+)$"
)
_LOCATION_HINT = re.compile(
    r"(?i)\b(audit[oó]rio|auditorio|sala|salao|campus|online|remoto|zoom|meet\.google"
    r"|teatro|biblioteca|pr[ée]dio|predio|bloco|lab(?:orat[oó]rio)?)\b"
)
_DATE_ISO = re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b")
_DATE_NUMERIC = re.compile(r"\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})\b")
_MONTHS = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
    "outubro": 10, "novembro": 11, "dezembro": 12,
}
_DATE_TEXT = re.compile(
    r"\b(\d{1,2})\s+de\s+([a-zç]+)(?:\s+de\s+(\d{4}))?\b", re.I
)
_TIME = re.compile(r"\b(\d{1,2})(?::|h)(\d{2})?\s*(?:h|hs|horas)?", re.I)
_LINK = re.compile(r"https?://[^\s<>\"')]+", re.I)
_LINK_EXTRACT = re.compile(r"\b(https?://[^\s<>\"')]+)(?=[),.;]?\s|$)", re.I)
_TITLE_PREFIX = re.compile(
    r"^\s*(?:re|fwd|fw|enc[:.]?|encaminhado|convite|convoca[çc][ãa]o|alerta|aviso|n[oó]tice)\s*:\s*",
    re.I,
)
_BRACKET_TAG = re.compile(r"^\s*\[[^\]]*\]\s*")
_FIELD_LINE = re.compile(
    r"(?im)^\s*(?:local|onde|localiza[çc][aã]o|endere[çc]o|data|dia|hora|"
    r"hor[áa]rio|inscri[çc][ãa]o|link|tipo|categoria|descri[çc][ãa]o)\s*[:\-–]\s*$"
)
_TYPE_KEYWORDS: list[tuple[tuple[str, ...], str]] = [
    (("hackathon", "hackatona", "maratona"), "Hackathon"),
    (("palestra", "confer[eê]ncia", "keynote", "semin[aá]rio", "seminario", "mesa redonda"), "Palestra"),
    (("workshop", "treinamento", "oficina", "curso", "laboratorio", "lab"), "Workshop"),
]

_DESCRIPTION_MAX = 2000


class InsufficientDataError(Exception):
    """E-mail sem os dados obrigatórios do evento (critério da US 4.1)."""

    def __init__(self, missing: list[str]) -> None:
        self.missing = list(missing)
        super().__init__(f"dados insuficientes: {', '.join(self.missing)}")


@dataclass
class ParsedEvent:
    """Evento extraído do e-mail — ainda não validado quanto ao futuro (US 4.4)."""

    title: str
    date: dt.date
    time: dt.time
    location: str
    description: str
    event_type: str = "Outro"
    registration_link: str = ""
    missing: list[str] = field(default_factory=list)


def _clean(text: str) -> str:
    """Impede que quebras de linha/fontes no e-mail quebrem as expressões."""
    text = text.replace("\r\n", "\n")
    return html.unescape(text)


def _subject_to_plain(subject: str) -> str:
    """Remove acentos e coloca em minúsculas apenas para casar padrões."""
    mapping = str.maketrans(
        "áàâãäéèêëíìîïóòôõöúùûüçÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ",
        "aaaaaeeeeiiiiooooouuuucAAAAAEEEEIIIIOOOOOUUUUC",
    )
    return subject.translate(mapping).lower()


def _extract_title(subject: str, body: str) -> str:
    title = _clean(subject or "").strip()
    for _ in range(5):
        new = _TITLE_PREFIX.sub("", title)
        new = _BRACKET_TAG.sub("", new)
        if new == title:
            break
        title = new
    title = title.strip(" \t-–:()[]")
    if title:
        return title
    for line in (body or "").splitlines():
        line = _clean(line).strip()
        if line:
            return line[:200]
    return ""


def _extract_date(text: str) -> dt.date | None:
    text = _clean(text)
    m = _DATE_ISO.search(text)
    if m:
        return _safe_date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = _DATE_NUMERIC.search(text)
    if m:
        day, month, year = m.group(1), m.group(2), m.group(3)
        if len(year) == 2:
            year = "20" + year
        return _safe_date(int(year), int(month), int(day))
    for m in _DATE_TEXT.finditer(text):
        day, month_word, year = m.group(1), _subject_to_plain(m.group(2)), m.group(3)
        month = _MONTHS.get(month_word)
        if month is None:
            continue
        return _safe_date(int(year) if year else dt.date.today().year, month, int(day))
    return None


def _safe_date(year: int, month: int, day: int) -> dt.date | None:
    try:
        return dt.date(year, month, day)
    except ValueError:
        return None


def _extract_time(text: str) -> dt.time | None:
    for m in _TIME.finditer(_clean(text)):
        hour, minute = int(m.group(1)), int(m.group(2) or 0)
        try:
            return dt.time(hour, minute)
        except ValueError:
            continue
    return None


def _extract_location(subject: str, body: str) -> str:
    text = _clean(body)
    m = _LOCATION_LABELED.search(text)
    if m:
        return m.group(1).strip().strip("-–:")[:200]
    for line in text.splitlines():
        line = line.strip()
        if _LOCATION_HINT.search(line) and len(line) <= 200:
            return line
    return ""


def _extract_type(subject: str, body: str) -> str:
    text = _subject_to_plain(f"{subject} {body}")
    for keywords, event_type in _TYPE_KEYWORDS:
        if any(re.search(rf"\b{kw}\b", text) for kw in keywords):
            return event_type
    return "Outro"


def _first_link(subject: str, body: str) -> str:
    m = _LINK_EXTRACT.search(_clean(f"{subject}\n{body}"))
    if not m:
        return ""
    return m.group(0).rstrip("),.;")


def _extract_description(title: str, body: str) -> str:
    text = _link_invisible(title + "\n" + body)
    text = _LOCATION_LABELED.sub("", text)
    text = _FIELD_LINE.sub("", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    description = next(
        (p for p in paragraphs if p),
        title,
    )
    description = re.sub(r"\s+", " ", description)
    if len(description) > _DESCRIPTION_MAX:
        description = description[:_DESCRIPTION_MAX].rstrip() + "…"
    return description


def _link_invisible(text: str) -> str:
    """Remove URLs do texto usado para descrição (falta só o texto visível)."""
    return re.sub(r"https?://[^\s<>\"')]+", " ", text, flags=re.I)


def parse_email(subject: str, body: str) -> ParsedEvent:
    """Extrai o evento de um e-mail ou levanta InsufficientDataError.

    Campos obrigatórios (título, data, hora, local) ausentes → exceção que o
    serviço transforma em log de status "ignorado" (Gherkin da US 4.1).
    """
    title = _extract_title(subject, body)
    date = _extract_date(f"{subject}\n{body}")
    time_ = _extract_time(f"{subject}\n{body}")
    location = _extract_location(subject, body)

    missing = [
        name
        for name, value in {
            "title": title,
            "date": date,
            "time": time_,
            "location": location,
        }.items()
        if not value
    ]
    if missing:
        raise InsufficientDataError(missing)

    return ParsedEvent(
        title=title,
        date=date,
        time=time_,
        location=location,
        description=_extract_description(title, body),
        event_type=_extract_type(subject, body),
        registration_link=_first_link(subject, body),
    )