import datetime

from fastapi import Depends, HTTPException, status

from app.core.config import Settings, get_settings
from app.schemas.predict import (
    BatchPredictItem,
    BatchPredictResponse,
    PredictResponse,
    SequencePredictResponse,
)
from ml import inference
from ml.data import InsufficientDataError


class PredictionService:
    """Orquestra o pipeline de inferência (ml/) e traduz erros de domínio em HTTPException."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def predict_single(self, symbol: str) -> PredictResponse:
        try:
            price, last_date = inference.predict_next_close(symbol, self.settings)
        except InsufficientDataError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
        return PredictResponse(
            symbol=symbol,
            predicted_close=price,
            last_trading_date=last_date,
            look_back=self.settings.look_back,
        )

    def predict_batch(self, symbols: list[str]) -> BatchPredictResponse:
        results: dict[str, BatchPredictItem] = {}
        for symbol in symbols:
            try:
                price, last_date = inference.predict_next_close(symbol, self.settings)
                results[symbol] = BatchPredictItem(predicted_close=price, last_trading_date=last_date)
            except InsufficientDataError as exc:
                results[symbol] = BatchPredictItem(error=str(exc))
        return BatchPredictResponse(results=results, generated_at=datetime.datetime.utcnow())

    def predict_sequence(self, symbol: str, days_ahead: int) -> SequencePredictResponse:
        try:
            preds = inference.predict_sequence(symbol, days_ahead, self.settings)
        except InsufficientDataError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
        return SequencePredictResponse(symbol=symbol, days_ahead=days_ahead, predictions=preds)


def get_prediction_service(settings: Settings = Depends(get_settings)) -> PredictionService:
    return PredictionService(settings)
