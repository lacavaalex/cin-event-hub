"""Router de extração de e-mails — US 4.1 (extração) + US 4.2 (IA/alertas) + US 4.4.

`POST /extraction/run` dispara manualmente um ciclo (útil para a primeira
autorização do OAuth e para validar os critérios de aceite). A varredura
periódica é feita pelo job agendado (``scheduler.py``).

`GET /extraction/alerts` expõe os e-mails que a IA marcou como "não processados"
(critério de aceite da US 4.2) e os eventos descartados pela validação autónoma
("Extração Incompleta", US 4.4). É um recorte enxuto de alertas — o dashboard
completo de monitoramento é a US 4.3.
`GET /extraction/status` expõe o resumo operacional para o painel "Status de
Extração" (US 4.3): contagens por status, total processado, últimos processados,
erros recentes e estado da última execução.
"""

from dataclasses import asdict

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.database import get_db
from app.schemas.extracao import (
    ExtractionAlertRead,
    ExtractionRunResponse,
    ExtractionStatusResponse,
)
from app.services.extracao_email.extraction_service import (
    get_status as get_extraction_status,
    list_alerts as get_extraction_alerts,
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
    ``extracao``.
    Exige token JWT de administrador.
    """
    summary = run_extraction(db)
    return ExtractionRunResponse(**asdict(summary))


@router.get(
    "/alerts",
    response_model=list[ExtractionAlertRead],
    dependencies=[Depends(get_current_admin)],
)
def list_alerts(
    limit: int = Query(50, ge=1, le=200, description="Máximo de alertas retornados"),
    db: Session = Depends(get_db),
):
    """Lista os e-mails não publicados para curadoria do administrador.

    Critério de aceite da US 4.2 (alerta ao administrador) + US 4.4 (eventos
    descartados pela validação autónoma). Inclui o status legado
    ``nao_processado`` para registos anteriores à validação. Exige token JWT.
    """
    return get_extraction_alerts(db, limit=limit)


@router.get(
    "/status",
    response_model=ExtractionStatusResponse,
    dependencies=[Depends(get_current_admin)],
)
def status(
    limit: int = Query(20, ge=1, le=200, description="Máximo de registros recentes por lista"),
    db: Session = Depends(get_db),
):
    """Retorna o resumo operacional da extração para o painel do administrador (US 4.3)."""
    return get_extraction_status(db, limit=limit)
