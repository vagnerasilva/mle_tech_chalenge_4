import datetime
import time

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.dependencies import get_db
from app.schemas.predict import (
    PredictResponse,
)
from app.services.monitoring_service import ModelMonitoringService
from ml import inference
from ml.data import InsufficientDataError


class PredictionService:
    """Orquestra o pipeline de inferência (ml/) e traduz erros de domínio em HTTPException."""

    def __init__(self, settings: Settings, db: Session | None = None):
        self.settings = settings
        self.db = db

    def predict_single(self, symbol: str) -> PredictResponse:
        try:
            price, prediction_date = inference.predict_next_close(symbol, self.settings)
        except InsufficientDataError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
        except Exception as exc:
            # Capturar erros de rate limit ou conexão do yfinance
            error_str = str(exc).lower()
            if 'rate limit' in error_str or 'too many requests' in error_str:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="yfinance rate limited. Please try again later."
                ) from exc
            # Outros erros
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate prediction. Please try again later."
            ) from exc
        
        # Salva a predição no banco de dados para monitoramento
        if self.db:
            self._save_prediction_metric(symbol, prediction_date, price)
        
        return PredictResponse(
            symbol=symbol,
            predicted_close=price,
            last_trading_date=prediction_date,
            look_back=self.settings.look_back,
        )

    def _save_prediction_metric(self, symbol: str, prediction_date: datetime.date, predicted_close: float) -> None:
        """
        Salva a predição na tabela de métricas para monitoramento posterior.
        
        Registra sempre como pendente, sem buscar ou calcular o preço real agora.
        A validação posterior preenche `actual_close` e as métricas.
        """
        if not self.db:
            return
        
        try:
            ModelMonitoringService.save_prediction_metrics(
                self.db,
                prediction_date=prediction_date,
                predicted_close=predicted_close,
                actual_close=None,
                metrics={
                    "mae": None,
                    "rmse": None,
                    "mape": None,
                    "directional_accuracy": None,
                    "error_percentage": None,
                },
            )
        except Exception as e:
            # Não falha a predição se houver erro ao salvar métrica
            print(f"Aviso: Não foi possível salvar métrica de predição: {e}")


def get_prediction_service(
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> PredictionService:
    return PredictionService(settings, db)
