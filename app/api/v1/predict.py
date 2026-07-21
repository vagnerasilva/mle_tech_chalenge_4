from fastapi import APIRouter, Depends

from app.schemas.predict import (
    PredictResponse,
)
from app.services.prediction_service import PredictionService, get_prediction_service

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post(
    "/next_close",
    response_model=PredictResponse,
    summary="Prevê o fechamento do próximo pregão",
)
def predict_next_close(service: PredictionService = Depends(get_prediction_service)
) -> PredictResponse:
    """
    Busca automaticamente, via `yfinance`, os últimos `look_back` (30) pregões
    de `symbol` e aplica o mesmo pipeline do treino — `log1p` → `StandardScaler`
    → janela deslizante OHLCV → LSTM → `inverse_transform` + `expm1` — para
    prever o preço de fechamento (`Close`) do próximo pregão.

    O modelo foi treinado especificamente para **BBD** (Bradesco ADR — NYSE),
    conforme `docs/documentacao_lstm_tech_challenge.md`. Qualquer ticker aceito
    pelo `yfinance` pode ser enviado, mas a qualidade da previsão só foi
    validada para BBD — outros ativos podem ter erro maior.

    Exemplo (equivalente ao `prever_proximo_dia()` do notebook de referência):
    ```
    POST /api/v1/predict/next_close
    ```
    """
    return service.predict_single("BBD")
