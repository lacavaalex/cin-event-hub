"""Router de extração de e-mails — US 4.1 (extração) + US 4.2 (IA/alertas) + US 4.4.

`POST /extraction/run` dispara manualmente um ciclo (útil para a primeira
autorização do OAuth e para validar os critérios de aceite). A varredura
periódica é feita pelo job agendado (``scheduler.py``).

`GET /extraction/alerts` expõe os e-mails que a IA marcou como "não processados"
(critério de aceite da US 4.2) e os eventos descartados pela validação autónoma
("Extração Incompleta", US 4.4). É um recorte enxuto de alertas — o dashboard
completo de monitoramento é a US 4.3.
"""

from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.database import get_db
from app.repositories import extraction_log_repository
from app.schemas.extracao import ExtractionAlertRead, ExtractionRunResponse
from app.services.extracao_email.extraction_service import (
    STATUS_EXTRACAO_INCOMPLETA,
    STATUS_NAO_PROCESSADO,
    run_extraction,
)

router = APIRouter(prefix="/extraction", tags=["extraction"])


@router.post(
    "/run",
    response_model=ExtractionRunResponse,
    dependencies=[Depends(get_current_admin)],
)
def run(db: Session = Depends(get_db)):
    """Executa um ciclo de extração de e-mails e insere eventos.

    Retorna quantos e-mails foram extraídos pelo parser (``processed``), pela IA
    (``processed_ia``), ignorados, não processados (alertas), descartados pela
    validação autónoma (``discarded``) e com erro — espelhando os logs da tabela
    ``extraction_logs``.
    Exige token JWT de administrador.
    """
    summary = run_extraction(db)
    return ExtractionRunResponse(**asdict(summary))


@router.get(
    "/alerts",
    response_model=list[ExtractionAlertRead],
    dependencies=[Depends(get_current_admin)],
)
def list_alerts(limit: int = 50, db: Session = Depends(get_db)):
    """Lista os e-mails não publicados para curadoria do administrador.

    Critério de aceite da US 4.2 (alerta ao administrador) + US 4.4 (eventos
    descartados pela validação autónoma). Inclui o status legado
    ``nao_processado`` para registos anteriores à validação. Exige token JWT.
    """
    return extraction_log_repository.list_by_statuses(
        db,
        [STATUS_EXTRACAO_INCOMPLETA, STATUS_NAO_PROCESSADO],
        limit,
    )
