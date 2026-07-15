import datetime

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
            price, last_date = inference.predict_next_close(symbol, self.settings)
        except InsufficientDataError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
        
        # Salva a predição no banco de dados para monitoramento
        if self.db:
            self._save_prediction_metric(symbol, last_date, price)
        
        return PredictResponse(
            symbol=symbol,
            predicted_close=price,
            last_trading_date=last_date,
            look_back=self.settings.look_back,
        )

    def _save_prediction_metric(self, symbol: str, prediction_date: datetime.date, predicted_close: float) -> None:
        """
        Salva a predição na tabela de métricas para monitoramento posterior.
        
        Tenta buscar o preço real do yfinance para calcular erro imediatamente,
        mas continua mesmo se a data ainda não estiver disponível (registra como pending).
        """
        if not self.db:
            return
        
        try:
            # Tenta buscar preço real para hoje/próximo dia
            actual_price = ModelMonitoringService.get_actual_price(prediction_date)
            
            if actual_price:
                # Se encontrou preço real, calcula métricas
                metrics = ModelMonitoringService.calculate_metrics(predicted_close, actual_price)
            else:
                # Senão, salva com preço real como None (será preenchido depois na validação)
                metrics = {
                    "mae": None,
                    "rmse": None,
                    "mape": None,
                    "directional_accuracy": None,
                    "error_percentage": None,
                }
            
            # Salva no banco
            ModelMonitoringService.save_prediction_metrics(
                self.db,
                prediction_date=prediction_date,
                predicted_close=predicted_close,
                actual_close=actual_price,
                metrics=metrics,
            )
        except Exception as e:
            # Não falha a predição se houver erro ao salvar métrica
            print(f"Aviso: Não foi possível salvar métrica de predição: {e}")


def get_prediction_service(
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> PredictionService:
    return PredictionService(settings, db)
