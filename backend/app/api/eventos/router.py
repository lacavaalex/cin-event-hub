"""Router de eventos — rotas de criação, listagem, edição e exclusão.

POST /events       → cria evento (US 2.1, protegida por JWT)
GET  /events       → lista eventos ativos (US 3.1, pública)
GET  /events/{id}  → busca evento por ID (US 2.2)
PUT  /events/{id}  → edita evento (US 2.2)
DELETE /events/{id} → exclui evento (US 2.3)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.database import get_db
from app.schemas.event import EventCreate, EventRead
from app.schemas.events.schemas import EventRead as EventReadAlb, EventUpdate
from app.services.event_service import PastEventDateError, create_event, list_events
from app.services.events import service

router = APIRouter(prefix="/events", tags=["events"])


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


# -- Busca por ID (US 2.2) --

@router.get("/{event_id}", response_model=EventReadAlb)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Busca um evento pelo ID."""
    try:
        return service.get_event(db, event_id)
    except service.EventNotFoundError:
        raise HTTPException(status_code=404, detail="Evento não encontrado")


# -- Edição (US 2.2) --

@router.put("/{event_id}", response_model=EventReadAlb)
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db)):
    """Atualiza um evento existente (US 2.2)."""
    try:
        return service.update_event(db, event_id, payload)
    except service.EventNotFoundError:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    except service.PastEventDateError:
        raise HTTPException(
            status_code=422, detail="A data do evento não pode estar no passado"
        )


# -- Exclusão (US 2.3) --

@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Exclui um evento (US 2.3). 204 = sem corpo na resposta."""
    try:
        service.delete_event(db, event_id)
    except service.EventNotFoundError:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
