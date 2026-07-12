from fastapi import APIRouter, HTTPException

from app.models.predict import PredictRequest, PredictResponse
from ml.data import DataCollectionError
from ml.inference import InsufficientDataError, ModelNotLoadedError
from app.services import model_service
from app.utils.constants import logger

router = APIRouter()


@router.post("", response_model=PredictResponse)
def predict(payload: PredictRequest):
    """Prevê o(s) próximo(s) preço(s) de fechamento.

    Opção A: informe `symbol` — a API busca os dados mais recentes via yfinance.
    Opção B: informe `historical_data` — a API usa a série fornecida pelo cliente.
    """
    logger.info(f"Predição solicitada: symbol={payload.symbol} days_ahead={payload.days_ahead}")
    try:
        return model_service.predict(payload)
    except ModelNotLoadedError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except InsufficientDataError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except DataCollectionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
