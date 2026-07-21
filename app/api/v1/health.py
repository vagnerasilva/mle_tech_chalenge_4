from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.health import HealthResponse, ReadinessResponse
from ml.model import artifacts_available

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    model_loaded = artifacts_available(settings.model_path, settings.scaler_path)
    return HealthResponse(status="ok", model_loaded=model_loaded)


@router.get("/readiness", response_model=ReadinessResponse)
def readiness_check(settings: Settings = Depends(get_settings)) -> ReadinessResponse:
    if artifacts_available(settings.model_path, settings.scaler_path):
        return ReadinessResponse(ready=True)
    return ReadinessResponse(
        ready=False,
        detail="Artefatos do modelo (modelo_lstm.keras / scaler.pkl) não encontrados.",
    )
