from fastapi import APIRouter, HTTPException

from app.models.stock import MetricsResponse, ModelInfoResponse, TrainRequest, TrainResponse
from app.services import model_service
from app.services.data_service import DataCollectionError
from app.utils.constants import logger

router = APIRouter()


@router.get("/info", response_model=ModelInfoResponse)
def model_info():
    """Metadados do modelo atualmente carregado (ticker, período, features, métricas)."""
    try:
        return model_service.get_model_info()
    except model_service.ModelNotLoadedError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/metrics", response_model=MetricsResponse)
def model_metrics():
    """Métricas de avaliação (MAE, RMSE, MAPE, loss) do modelo atualmente carregado."""
    try:
        return model_service.get_model_metrics()
    except model_service.ModelNotLoadedError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.post("/train", response_model=TrainResponse)
def train_model(payload: TrainRequest):
    """Coleta dados, treina, avalia e salva um novo modelo LSTM (execução síncrona)."""
    logger.info(f"Iniciando treinamento para {payload.symbol} ({payload.start_date} -> {payload.end_date})")
    try:
        return model_service.train(payload)
    except DataCollectionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
