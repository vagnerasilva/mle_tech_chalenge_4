from fastapi import APIRouter

from app.models.stock import HealthResponse
from app.services import model_service
from app.settings import settings
from app.utils.constants import logger

router = APIRouter()


@router.get("", response_model=HealthResponse)
def health_check():
    """Status da API, se o modelo LSTM está carregado e a versão em uso."""
    logger.info("Verificando saúde da API e do modelo")
    return model_service.get_health(environment=settings.ENVIRONMENT)
