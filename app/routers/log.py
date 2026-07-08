from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services import log
from app.dependencies import get_db
from app.utils.constants import logger

router = APIRouter()


@router.get("/api_logs")
def obter_logs(
    db: Session = Depends(get_db)
):
    """Obtém todos os logs de API"""
    logger.info("Obtendo logs de API")
    return log.get_logs(db)
