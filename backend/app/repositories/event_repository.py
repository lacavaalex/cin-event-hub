"""Repositório de eventos — acesso direto ao banco de dados.

Mantém compatibilidade com o repositório da branch develop_alb (Albert),
adicionando as operações de criação (US 2.1) e listagem (US 3.1).
"""

import datetime as dt

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.texto import SIMILARIDADE_MINIMA, titulos_sao_similares
from app.models.event import Event

_PG_INT4_MAX = 2_147_483_647


def create(db: Session, event: Event) -> Event:
    """Persiste um novo evento no banco (US 2.1)."""
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_all(
    db: Session,
    limit: int = 20,
    offset: int = 0,
    min_date: dt.date | None = None,
) -> list[Event]:
    """Retorna uma página de eventos ativos em ordem cronológica (US 3.1, IESI-71).

    ``limit`` e ``offset`` viram LIMIT/OFFSET na query do PostgreSQL. A ordem é
    data, hora e id: o id desempata eventos no mesmo horário para que, entre uma
    página e outra, nenhum evento se repita ou fique de fora (sem ordem total,
    o PostgreSQL pode devolver linhas empatadas em qualquer ordem).

    Quando ``min_date`` é informado, exclui eventos cuja data limite
    (``COALESCE(end_date, date)``) já passou (US 5.1 / BE-041).
    """
    query = db.query(Event).filter(Event.status == "active")
    if min_date is not None:
        query = query.filter(func.coalesce(Event.end_date, Event.date) >= min_date)
    return (
        query
        .order_by(Event.date, Event.time, Event.id)
        .limit(limit)
        .offset(offset)
        .all()
    )


def count_active(db: Session, min_date: dt.date | None = None) -> int:
    """Conta os eventos ativos (base do total de páginas da listagem, IESI-70)."""
    query = db.query(func.count(Event.id)).filter(Event.status == "active")
    if min_date is not None:
        query = query.filter(func.coalesce(Event.end_date, Event.date) >= min_date)
    return query.scalar()


def find_active_duplicate_by_title_and_date(
    db: Session,
    title: str,
    event_date: dt.date,
    *,
    limite: float = SIMILARIDADE_MINIMA,
) -> Event | None:
    """Busca um evento ativo com o mesmo título (ou similar) e a mesma data (IESI-76).

    O filtro ``status='active' AND date=:data`` usa o índice parcial
    ``ix_events_ativos_data`` e reduz os candidatos a um único dia; a comparação
    de título (normalização + similaridade) acontece em memória para não exigir
    a extensão ``pg_trgm``. Ordenar por id torna o resultado determinístico:
    quando vários títulos similares existem, o mais antigo é devolvido.
    """
    candidatos = (
        db.query(Event)
        .filter(Event.status == "active", Event.date == event_date)
        .order_by(Event.id)
        .all()
    )
    for candidato in candidatos:
        if titulos_sao_similares(title, candidato.title, limite=limite):
            return candidato
    return None


def get_by_id(db: Session, event_id: int) -> Event | None:
    """Busca um evento pelo ID."""
    if event_id < 1 or event_id > _PG_INT4_MAX:
        return None
    return db.get(Event, event_id)


def get_expired_events(db: Session, reference_date: dt.date) -> list[Event]:
    """Retorna todos os eventos cuja data limite é anterior à data de referência (US 5.1)."""
    return (
        db.query(Event)
        .filter(func.coalesce(Event.end_date, Event.date) < reference_date)
        .all()
    )


