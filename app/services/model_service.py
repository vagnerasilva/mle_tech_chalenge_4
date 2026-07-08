"""Camada de serviço entre os routers da API e o pacote `ml/`.

Mantém uma única instância de `StockForecastService` em memória (carregada
lazily no primeiro uso e forçada no startup da aplicação — ver `app/app.py`)
para evitar recarregar o modelo Keras a cada request.
"""

from datetime import datetime, timezone

from ml.data import DataCollectionError
from ml.inference import InsufficientDataError, ModelNotLoadedError, StockForecastService
from ml.model import run_training_pipeline

_service: StockForecastService | None = None


def get_service() -> StockForecastService:
    global _service
    if _service is None:
        _service = StockForecastService()
    return _service


def get_health(environment: str) -> dict:
    svc = get_service()
    return {
        "status": "ok",
        "model_loaded": svc.loaded,
        "model_version": svc.model_version if svc.loaded else None,
        "current_time": datetime.now(timezone.utc).isoformat(),
        "environment": environment,
    }


def get_model_info() -> dict:
    svc = get_service()
    if not svc.loaded:
        raise ModelNotLoadedError("Nenhum modelo treinado/carregado ainda.")
    meta = svc.metadata
    return {
        "model_name": meta["model_name"],
        "model_type": meta["model_type"],
        "symbol": meta["symbol"],
        "data_start_date": meta["data_start_date"],
        "data_end_date": meta["data_end_date"],
        "sequence_length": meta["sequence_length"],
        "features": meta["features"],
        "metrics": meta["metrics"],
        "trained_at": meta["trained_at"],
        "model_path": meta["model_path"],
        "model_version": meta["model_version"],
    }


def get_model_metrics() -> dict:
    svc = get_service()
    if not svc.loaded:
        raise ModelNotLoadedError("Nenhum modelo treinado/carregado ainda.")
    meta = svc.metadata
    metrics = meta.get("metrics", {})
    dataset = meta.get("dataset", {})
    return {
        "mae": metrics.get("mae"),
        "rmse": metrics.get("rmse"),
        "mape": metrics.get("mape"),
        "directional_accuracy": metrics.get("directional_accuracy"),
        "final_loss": metrics.get("final_loss"),
        "final_val_loss": metrics.get("final_val_loss"),
        "trained_at": meta.get("trained_at"),
        "dataset_size": dataset.get("total_samples", 0),
    }


def train(payload) -> dict:
    metadata = run_training_pipeline(
        symbol=payload.symbol,
        start_date=payload.start_date,
        end_date=payload.end_date,
        sequence_length=payload.sequence_length,
        epochs=payload.epochs,
        batch_size=payload.batch_size,
    )
    # Recarrega o serviço em memória com o modelo recém-treinado.
    get_service().reload()
    return {
        "model_name": metadata["model_name"],
        "model_version": metadata["model_version"],
        "symbol": metadata["symbol"],
        "sequence_length": metadata["sequence_length"],
        "metrics": metadata["metrics"],
        "trained_at": metadata["trained_at"],
    }


def predict(payload) -> dict:
    svc = get_service()
    historical_data = (
        [point.model_dump() for point in payload.historical_data]
        if payload.historical_data
        else None
    )
    return svc.predict(
        symbol=payload.symbol,
        historical_data=historical_data,
        days_ahead=payload.days_ahead,
    )


__all__ = [
    "DataCollectionError",
    "InsufficientDataError",
    "ModelNotLoadedError",
    "get_service",
    "get_health",
    "get_model_info",
    "get_model_metrics",
    "train",
    "predict",
]
