from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.events.schemas import EventRead, EventUpdate
from app.services.events import service

# TODO(E1 / US 1.1): proteger as rotas de escrita (PUT e DELETE) com o login
# do admin (JWT).
router = APIRouter(prefix="/events", tags=["events"])


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Busca um evento pelo ID. Usado para preencher o formulário de edição."""
    try:
        return service.get_event(db, event_id)
    except service.EventNotFoundError:
        raise HTTPException(status_code=404, detail="Evento não encontrado")


@router.put("/{event_id}", response_model=EventRead)
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db)):
    """Atualiza os detalhes de um evento existente (US 2.2)."""
    try:
        return service.update_event(db, event_id, payload)
    except service.EventNotFoundError:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    except service.PastEventDateError:
        raise HTTPException(
            status_code=422, detail="A data do evento não pode estar no passado"
        )


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Exclui manualmente um evento (US 2.3).

    204 No Content: deu certo e não há corpo na resposta.
    A confirmação do usuário acontece no frontend (modal); a API só executa.
    """
    try:
        service.delete_event(db, event_id)
    except service.EventNotFoundError:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
