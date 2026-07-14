from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.logs import ApiLogEntry
from app.services import log_service

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("", response_model=list[ApiLogEntry], summary="Consulta o histórico de acessos à API")
def list_logs(
    limit: int = Query(default=500, ge=1, le=500, description="Quantidade máxima de registros, mais recentes primeiro"),
    db: Session = Depends(get_db),
) -> list[ApiLogEntry]:
    """
    Retorna os registros de auditoria (método, rota, status, tempo de
    resposta, IP, data/hora) gravados automaticamente para toda requisição
    da API por um middleware global (ver `app/main.py`).

    Mesmo padrão de logging usado no `mle_tech_chalenge_1`
    (`app/services/log.py` / `app/routers/log.py`), adaptado para este
    projeto: um middleware grava cada requisição em background numa tabela
    SQLite (`api_logs`), e esta rota consulta essa tabela.
    """
    return log_service.get_logs(db, limit=limit)
