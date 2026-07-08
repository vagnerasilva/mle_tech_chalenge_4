from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.stock import MonitoringResponse
from app.services import monitoring_service

router = APIRouter()


@router.get("/metrics", response_model=MonitoringResponse)
def monitoring_metrics(db: Session = Depends(get_db)):
    """Métricas básicas de uso da API: total de chamadas, tempo médio de resposta,
    contagem por status HTTP e últimas predições (sem expor payloads)."""
    return monitoring_service.get_monitoring_metrics(db)
