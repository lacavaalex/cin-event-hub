"""Router de eventos — POST /events (US 2.1, IESI-32) + GET /events (US 3.1).

As rotas de escrita (POST) são protegidas por autenticação JWT (US 1.1).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.database import get_db
from app.schemas.event import EventCreate, EventRead
from app.services.event_service import PastEventDateError, create_event, list_events

router = APIRouter(prefix="/events", tags=["events"])


@router.post(
    "",
    response_model=EventRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
)
def create(payload: EventCreate, db: Session = Depends(get_db)):
    """Cria um novo evento (US 2.1).

    **Critérios de Aceite:**
    - Campos obrigatórios preenchidos → evento criado e retornado com HTTP 201
    - Campo obrigatório vazio → HTTP 422 (validação Pydantic)
    - Data no passado → HTTP 422 com mensagem de aviso
    - Requer token JWT válido (Header ``Authorization: Bearer <token>``)
    """
    try:
        event = create_event(db, payload)
    except PastEventDateError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A data do evento não pode estar no passado",
        )

    return event


@router.get("", response_model=list[EventRead])
def list_all(db: Session = Depends(get_db)):
    """Lista todos os eventos ativos (US 3.1).

    Rota pública — não exige autenticação.
    """
    return list_events(db)
