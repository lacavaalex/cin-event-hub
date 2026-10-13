"""Router de extração de e-mails — POST /extraction/run.

O endpoint permite disparar manualmente um ciclo de extração (útil para a
primeira autorização do OAuth e para validação do critério de aceite). A
varredura periódica é feita pelo job agendado (scheduler.py).
"""

from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.database import get_db
from app.schemas.extracao import ExtractionRunResponse
from app.services.extracao_email.extraction_service import run_extraction

router = APIRouter(prefix="/extraction", tags=["extraction"])


@router.post(
    "/run",
    response_model=ExtractionRunResponse,
    dependencies=[Depends(get_current_admin)],
)
def run(db: Session = Depends(get_db)):
    """Executa um ciclo de extração de e-mails e insere eventos.

    Retorna quantos e-mails foram processados, ignorados (sem dados
    obrigatórios) e com erro — espelhando os logs da tabela ``extraction_logs``.
    Exige token JWT de administrador.
    """
    summary = run_extraction(db)
    return ExtractionRunResponse(**asdict(summary))