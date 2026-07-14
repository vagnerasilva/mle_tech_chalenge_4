import datetime
import uuid

import numpy as np
import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session

from app.models.metrics import ModelMetrics


class ModelMonitoringService:
    """
    Serviço para monitorar o desempenho do modelo LSTM.
    
    Responsabilidades:
    - Calcular métricas de predição vs valor real
    - Armazenar métricas no banco de dados
    - Comparar predições com dados do yfinance
    """

    @staticmethod
    def calculate_metrics(
        predicted_close: float,
        actual_close: float,
    ) -> dict:
        """
        Calcula métricas de erro entre predição e valor real.
        
        Args:
            predicted_close: Preço predito pelo modelo
            actual_close: Preço real do ativo (yfinance)
        
        Returns:
            Dict com métricas: mae, rmse, mape, directional_accuracy, error_percentage
        """
        error = actual_close - predicted_close
        abs_error = abs(error)
        
        # MAE (Mean Absolute Error)
        mae = abs_error
        
        # RMSE (Root Mean Squared Error)
        rmse = np.sqrt(error ** 2)
        
        # MAPE (Mean Absolute Percentage Error)
        mape = (abs_error / actual_close * 100) if actual_close != 0 else 0.0
        
        # Acurácia Direcional: 1.0 se a predição acertou a direção do movimento
        # (comparado com last_price, não há comparação com dia anterior)
        directional_accuracy = 1.0 if error * (predicted_close - actual_close) <= 0 else 0.0
        
        # Erro percentual
        error_percentage = (error / actual_close * 100) if actual_close != 0 else 0.0
        
        return {
            "mae": float(mae),
            "rmse": float(rmse),
            "mape": float(mape),
            "directional_accuracy": float(directional_accuracy),
            "error_percentage": float(error_percentage),
        }

    @staticmethod
    def save_prediction_metrics(
        db: Session,
        prediction_date: datetime.date,
        predicted_close: float,
        actual_close: float,
        metrics: dict,
    ) -> ModelMetrics:
        """
        Salva as métricas da predição no banco de dados para BBD.
        
        Args:
            db: Sessão SQLAlchemy
            prediction_date: Data da predição
            predicted_close: Preço predito
            actual_close: Preço real
            metrics: Dict com métricas calculadas
        
        Returns:
            Objeto ModelMetrics criado
        """
        SYMBOL = "BBD"
        metric_record = ModelMetrics(
            id=str(uuid.uuid4()),
            symbol=SYMBOL,
            prediction_date=prediction_date,
            actual_date=datetime.date.today(),
            predicted_close=predicted_close,
            actual_close=actual_close,
            mae=metrics["mae"],
            rmse=metrics["rmse"],
            mape=metrics["mape"],
            directional_accuracy=metrics["directional_accuracy"],
            error_percentage=metrics["error_percentage"],
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        db.add(metric_record)
        db.commit()
        db.refresh(metric_record)
        return metric_record

    @staticmethod
    def get_actual_price(target_date: datetime.date) -> float | None:
        """
        Busca o preço de fechamento real do yfinance para uma data específica para BBD.
        
        Args:
            target_date: Data desejada
        
        Returns:
            Preço de fechamento (Close) ou None se não encontrado
        """
        SYMBOL = "BBD"
        try:
            # Busca dados do dia anterior ao target_date até 5 dias depois
            start = target_date - datetime.timedelta(days=1)
            end = target_date + datetime.timedelta(days=5)
            
            data = yf.download(SYMBOL, start=start, end=end, progress=False)
            
            if data.empty:
                return None
            
            # Normaliza colunas (yfinance retorna MultiIndex para alguns símbolos)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            # Procura pelo preço no target_date
            if isinstance(data.index, pd.DatetimeIndex):
                for idx in data.index:
                    if idx.date() == target_date:
                        return float(data.loc[idx, "Close"])
            
            return None
            
        except Exception as e:
            print(f"Erro ao buscar preço real para {SYMBOL} em {target_date}: {e}")
            return None

    @staticmethod
    def get_metrics_by_date_range(
        db: Session,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> list[ModelMetrics]:
        """
        Busca métricas registradas num intervalo de datas para BBD.
        
        Args:
            db: Sessão SQLAlchemy
            start_date: Data inicial (inclusive)
            end_date: Data final (inclusive)
        
        Returns:
            Lista de registros ModelMetrics
        """
        SYMBOL = "BBD"
        query = db.query(ModelMetrics)
        query = query.filter(ModelMetrics.symbol == SYMBOL)
        
        if start_date:
            query = query.filter(ModelMetrics.prediction_date >= start_date)
        
        if end_date:
            query = query.filter(ModelMetrics.prediction_date <= end_date)
        
        return query.order_by(ModelMetrics.prediction_date.desc()).all()

    @staticmethod
    def get_summary_stats(
        db: Session,
    ) -> dict:
        """
        Calcula estatísticas agregadas das métricas para BBD.
        
        Args:
            db: Sessão SQLAlchemy
        
        Returns:
            Dict com média de mae, rmse, mape, directional_accuracy
        """
        SYMBOL = "BBD"
        query = db.query(ModelMetrics)
        query = query.filter(ModelMetrics.symbol == SYMBOL)
        
        records = query.all()
        
        if not records:
            return {}
        
        mae_values = [r.mae for r in records if r.mae is not None]
        rmse_values = [r.rmse for r in records if r.rmse is not None]
        mape_values = [r.mape for r in records if r.mape is not None]
        dir_acc_values = [r.directional_accuracy for r in records if r.directional_accuracy is not None]
        
        return {
            "total_predictions": len(records),
            "avg_mae": float(np.mean(mae_values)) if mae_values else 0.0,
            "avg_rmse": float(np.mean(rmse_values)) if rmse_values else 0.0,
            "avg_mape": float(np.mean(mape_values)) if mape_values else 0.0,
            "avg_directional_accuracy": float(np.mean(dir_acc_values)) if dir_acc_values else 0.0,
            "min_mae": float(np.min(mae_values)) if mae_values else 0.0,
            "max_mae": float(np.max(mae_values)) if mae_values else 0.0,
            "min_mape": float(np.min(mape_values)) if mape_values else 0.0,
            "max_mape": float(np.max(mape_values)) if mape_values else 0.0,
        }
