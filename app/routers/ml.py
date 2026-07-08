from fastapi import APIRouter, HTTPException

from app.services import ml
from app.services.model_service import ModelNotLoadedError

router = APIRouter()


@router.get("/features")
def get_features():
    """Amostra dos dados pré-processados e metadados das features usadas pelo modelo."""
    try:
        return ml.get_features()
    except ModelNotLoadedError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
