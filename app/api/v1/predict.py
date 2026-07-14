from fastapi import APIRouter, Depends

from app.schemas.predict import (
    BatchPredictRequest,
    BatchPredictResponse,
    PredictRequest,
    PredictResponse,
    SequencePredictRequest,
    SequencePredictResponse,
)
from app.services.prediction_service import PredictionService, get_prediction_service

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post(
    "/single",
    response_model=PredictResponse,
    summary="Prevê o fechamento do próximo pregão",
)
def predict_single(
    payload: PredictRequest, service: PredictionService = Depends(get_prediction_service)
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
    POST /api/v1/predict/single
    {"symbol": "BBD"}
    ```
    """
    return service.predict_single(payload.symbol)


@router.post(
    "/batch",
    response_model=BatchPredictResponse,
    summary="Prevê o fechamento do próximo pregão para vários símbolos",
)
def predict_batch(
    payload: BatchPredictRequest, service: PredictionService = Depends(get_prediction_service)
) -> BatchPredictResponse:
    """
    Aplica a mesma previsão de `/predict/single` a uma lista de símbolos.
    Cada símbolo é resolvido de forma independente: se o `yfinance` não
    retornar pregões suficientes para um ticker (símbolo inválido, IPO
    recente, etc.), o erro fica isolado em `results[symbol].error` e não
    derruba os demais símbolos do lote.

    Exemplo:
    ```
    POST /api/v1/predict/batch
    {"symbols": ["BBD", "PETR4.SA"]}
    ```
    """
    return service.predict_batch(payload.symbols)


@router.post(
    "/sequence",
    response_model=SequencePredictResponse,
    summary="Prevê `days_ahead` pregões à frente (forecast recursivo)",
)
def predict_sequence(
    payload: SequencePredictRequest, service: PredictionService = Depends(get_prediction_service)
) -> SequencePredictResponse:
    """
    O modelo só foi treinado para prever 1 passo à frente (`Close` do dia
    seguinte). Para `days_ahead > 1`, cada previsão é realimentada como
    entrada do passo seguinte: `High = Low = Open = Close` previsto, e
    `Volume` é mantido no último valor observado — ver `ml/inference.py:predict_sequence`.
    Essa simplificação faz a previsão degradar com o horizonte; trate como
    tendência aproximada, não como previsão precisa dia a dia.

    Exemplo (3 pregões à frente para BBD):
    ```
    POST /api/v1/predict/sequence
    {"symbol": "BBD", "days_ahead": 3}
    ```
    """
    return service.predict_sequence(payload.symbol, payload.days_ahead)
