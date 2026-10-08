from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.Security import get_current_admin_id
from app.database.database import get_db
from app.schemas.events.schemas import EventCreate, EventRead, EventUpdate
from app.services.events import service

router = APIRouter(prefix="/events", tags=["events"])


@router.post(
    "",
    response_model=EventRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin_id)],
)
def create(payload: EventCreate, db: Session = Depends(get_db)):
    """Cria um novo evento (US 2.1). Requer autenticação JWT de admin."""
    try:
        return service.create_event(db, payload)
    except service.PastEventDateError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A data do evento não pode estar no passado",
        )


@router.get("", response_model=list[EventRead])
def list_all(db: Session = Depends(get_db)):
    """Lista todos os eventos ativos (US 3.1). Rota pública."""
    return service.list_events(db)


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Busca um evento pelo ID. Rota pública para detalhes e edição."""
    try:
        return service.get_event(db, event_id)
    except service.EventNotFoundError:
        raise HTTPException(status_code=404, detail="Evento não encontrado")


@router.put("/{event_id}", response_model=EventRead)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    _admin_id: int = Depends(get_current_admin_id),
):
    """Atualiza os detalhes de um evento existente (US 2.2). Requer admin."""
    try:
        return service.update_event(db, event_id, payload)
    except service.EventNotFoundError:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    except service.PastEventDateError:
        raise HTTPException(
            status_code=422, detail="A data do evento não pode estar no passado"
        )


@router.delete("/{event_id}", status_code=204)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    _admin_id: int = Depends(get_current_admin_id),
):
    """Exclui manualmente um evento (US 2.3).

    Requer admin. A confirmação do usuário acontece no frontend (modal);
    a API só executa.
    """
    try:
        service.delete_event(db, event_id)
    except service.EventNotFoundError:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
        