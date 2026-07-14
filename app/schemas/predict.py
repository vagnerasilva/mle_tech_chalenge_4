import datetime

from pydantic import BaseModel, ConfigDict, Field


class PredictRequest(BaseModel):
    symbol: str = Field(..., description="Ticker aceito pelo yfinance, ex.: 'PETR4.SA', 'BBD'")

    model_config = ConfigDict(
        json_schema_extra={
            # Mesmo símbolo (BBD) usado no treino do modelo — ver
            # docs/documentacao_lstm_tech_challenge.md, seção 8.2
            # (prever_proximo_dia). Outros tickers funcionam, mas a
            # qualidade da previsão não foi validada fora de BBD.
            "examples": [{"symbol": "BBD"}]
        }
    )


class PredictResponse(BaseModel):
    symbol: str
    predicted_close: float
    last_trading_date: datetime.date
    look_back: int

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "symbol": "BBD",
                    "predicted_close": 3.4482,
                    "last_trading_date": "2026-07-10",
                    "look_back": 30,
                }
            ]
        }
    )


class BatchPredictRequest(BaseModel):
    symbols: list[str] = Field(..., min_length=1)

    model_config = ConfigDict(json_schema_extra={"examples": [{"symbols": ["BBD", "PETR4.SA"]}]})


class BatchPredictItem(BaseModel):
    predicted_close: float | None = None
    last_trading_date: datetime.date | None = None
    error: str | None = None


class BatchPredictResponse(BaseModel):
    results: dict[str, BatchPredictItem]
    generated_at: datetime.datetime

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "results": {
                        "BBD": {"predicted_close": 3.4482, "last_trading_date": "2026-07-10", "error": None},
                        "PETR4.SA": {
                            "predicted_close": None,
                            "last_trading_date": None,
                            "error": "yfinance não retornou dados para 'PETR4.SA' entre ... e ...",
                        },
                    },
                    "generated_at": "2026-07-13T23:48:18.640903",
                }
            ]
        }
    )


class SequencePredictRequest(BaseModel):
    symbol: str
    days_ahead: int = Field(default=5, ge=1, le=60)

    model_config = ConfigDict(json_schema_extra={"examples": [{"symbol": "BBD", "days_ahead": 5}]})


class SequencePredictResponse(BaseModel):
    symbol: str
    days_ahead: int
    predictions: list[float]
    method: str = "recursive_close_only"
    note: str = (
        "Previsão recursiva: a partir do 2º passo, High/Low/Open assumem o "
        "Close previsto e o Volume é mantido no último valor observado. "
        "A qualidade da previsão degrada com o horizonte."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "symbol": "BBD",
                    "days_ahead": 3,
                    "predictions": [3.4482, 3.4003, 3.3657],
                    "method": "recursive_close_only",
                    "note": (
                        "Previsão recursiva: a partir do 2º passo, High/Low/Open assumem o "
                        "Close previsto e o Volume é mantido no último valor observado. "
                        "A qualidade da previsão degrada com o horizonte."
                    ),
                }
            ]
        }
    )
