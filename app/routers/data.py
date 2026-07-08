from fastapi import APIRouter, HTTPException

from app.models.stock import DataCollectRequest, DataCollectResponse
from app.services import data_service
from app.utils.constants import logger

router = APIRouter()


@router.post("/collect", response_model=DataCollectResponse)
def collect_data(payload: DataCollectRequest):
    """Coleta dados históricos de um ticker via yfinance e salva em data/raw/."""
    logger.info(f"Coletando dados de {payload.symbol} ({payload.start_date} -> {payload.end_date})")
    try:
        return data_service.collect(payload)
    except data_service.DataCollectionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
