from fastapi import APIRouter

from app.schemas.metrics import MetricsResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/latest", response_model=MetricsResponse)
def metrics_latest() -> MetricsResponse:
    """Métricas da avaliação offline no conjunto de teste (treinamento do modelo).

    Não são recalculadas em tempo real — ver
    docs/documentacao_lstm_tech_challenge.md, seção 6.
    """
    return MetricsResponse(
        symbol="BBD",
        mae=0.0297,
        rmse=0.0386,
        mape=1.94,
        directional_accuracy=40.31,
        source="avaliação offline no conjunto de teste (treinamento do modelo)",
    )
