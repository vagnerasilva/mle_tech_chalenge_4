import datetime

from sqlalchemy import Column, Date, DateTime, Float, String, create_engine
from sqlalchemy.orm import declarative_base

from app.models.base import Base


class ModelMetrics(Base):
    """
    Tabela para armazenar métricas de desempenho do modelo LSTM.
    
    Permite rastrear:
    - Predições (predicted_close) vs valores reais (actual_close)
    - Data de negociação (prediction_date)
    - Erro absoluto (mae), quadrático (rmse), percentual (mape)
    - Acurácia direcional (se a predição acertou a direção do movimento)
    """
    __tablename__ = "model_metrics"

    id = Column(String, primary_key=True)  # UUID ou similar
    symbol = Column(String(10), index=True)
    prediction_date = Column(Date, index=True)  # Data da predição
    actual_date = Column(Date)  # Data em que o preço real foi consultado

    # Valores de preço
    predicted_close = Column(Float)  # Preço predito pelo modelo
    actual_close = Column(Float)  # Preço real do yfinance

    # Métricas de erro
    mae = Column(Float)  # Mean Absolute Error
    rmse = Column(Float)  # Root Mean Squared Error
    mape = Column(Float)  # Mean Absolute Percentage Error
    directional_accuracy = Column(Float)  # 1.0 se direção correta, 0.0 se não
    error_percentage = Column(Float)  # Erro percentual: (pred - actual) / actual * 100

    # Metadados
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        actual_display = f"{self.actual_close:.4f}" if self.actual_close is not None else "None"
        mae_display = f"{self.mae:.4f}" if self.mae is not None else "None"
        return (
            f"<ModelMetrics {self.symbol} "
            f"pred_date={self.prediction_date} "
            f"pred={self.predicted_close:.4f} "
            f"actual={actual_display} "
            f"mae={mae_display}>"
        )
