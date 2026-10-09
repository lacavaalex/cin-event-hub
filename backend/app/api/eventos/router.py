"""Router de eventos — rotas de criação, listagem, edição, exclusão e favoritos.

POST /events                   → cria evento (US 2.1, protegida por JWT)
GET  /events                   → lista eventos ativos (US 3.1, pública)
GET  /events/{id}              → busca evento por ID (US 2.2)
PUT  /events/{id}              → edita evento (US 2.2, protegida por JWT)
DELETE /events/{id}            → exclui evento (US 2.3, protegida por JWT)
POST /events/{id}/favorite     → favorita evento (US 6.1)
DELETE /events/{id}/favorite   → desfavorita evento (US 6.1)
"""

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.database import get_db
from app.schemas.event import EventCreate, EventRead
from app.schemas.events.schemas import (
    EventRead as EventReadAlb,
    EventUpdate,
    FavoriteStatus,
)
from app.services.event_service import PastEventDateError, create_event, list_events
from app.services.events import service

router = APIRouter(prefix="/events", tags=["events"])


def get_current_user_id(x_user_id: int = Header(..., alias="X-User-Id")) -> int:
    """Obtém o ID do aluno pelo header enquanto não há autenticação de aluno."""
    return x_user_id


# -- Criação (US 2.1) --

@router.post(
    "",
    response_model=EventRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
)
def create(payload: EventCreate, db: Session = Depends(get_db)):
    """Cria um novo evento (US 2.1). Requer JWT."""
    try:
        event = create_event(db, payload)
    except PastEventDateError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A data do evento não pode estar no passado",
        )
    return event


# -- Listagem (US 3.1) --

@router.get("", response_model=list[EventRead])
def list_all(db: Session = Depends(get_db)):
    """Lista todos os eventos ativos. Rota pública."""
    return list_events(db)


# -- Favoritos (US 6.1) --

@router.post("/{event_id}/favorite", response_model=FavoriteStatus)
def favorite_event(
    event_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Favorita um evento de forma idempotente."""
    try:
        return service.favorite_event(db, user_id, event_id)
    except service.EventNotFoundError:
        raise HTTPException(status_code=404, detail="Evento não encontrado")


@router.delete("/{event_id}/favorite", response_model=FavoriteStatus)
def unfavorite_event(
    event_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Remove um favorito de forma idempotente."""
    return service.unfavorite_event(db, user_id, event_id)


# -- Busca por ID (US 2.2) --

@router.get("/{event_id}", response_model=EventReadAlb)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Busca um evento pelo ID."""
    try:
        return service.get_event(db, event_id)
    except service.EventNotFoundError:
        raise HTTPException(status_code=404, detail="Evento não encontrado")


# -- Edição (US 2.2) --

@router.put(
    "/{event_id}",
    response_model=EventReadAlb,
    dependencies=[Depends(get_current_admin)],
)
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db)):
    """Atualiza um evento existente (US 2.2). Requer autenticação de admin."""
    try:
        return service.update_event(db, event_id, payload)
    except service.EventNotFoundError:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    except service.PastEventDateError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A data do evento não pode estar no passado",
        )


# -- Exclusão (US 2.3) --

@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Exclui um evento (US 2.3). Requer autenticação de admin."""
    try:
        service.delete_event(db, event_id)
    except service.EventNotFoundError:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
