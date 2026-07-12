from pydantic import BaseModel, Field, model_validator


class HistoricalPoint(BaseModel):
    date: str = Field(..., description="Data no formato YYYY-MM-DD")
    close: float = Field(..., gt=0, description="Preço de fechamento")


class PredictRequest(BaseModel):
    symbol: str | None = Field(None, description="Ticker, ex.: BBD, AAPL, PETR4.SA")
    historical_data: list[HistoricalPoint] | None = Field(
        None, description="Série histórica fornecida pelo cliente (alternativa ao symbol)"
    )
    days_ahead: int = Field(1, ge=1, le=30, description="Quantos pregões à frente prever")

    @model_validator(mode="after")
    def _one_of_symbol_or_historical(self):
        if not self.symbol and not self.historical_data:
            raise ValueError("Informe 'symbol' ou 'historical_data'.")
        if self.symbol and self.historical_data:
            raise ValueError("Informe apenas um: 'symbol' OU 'historical_data', não os dois.")
        return self


class PredictionPoint(BaseModel):
    date: str
    predicted_close: float


class PredictResponse(BaseModel):
    symbol: str
    last_known_date: str
    prediction_date: str
    predicted_close: float
    days_ahead: int
    model_version: str
    sequence_length: int
    predictions: list[PredictionPoint]
