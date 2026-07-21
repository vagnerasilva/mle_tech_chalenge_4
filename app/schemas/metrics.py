from pydantic import BaseModel


class MetricsResponse(BaseModel):
    symbol: str
    mae: float
    rmse: float
    mape: float
    directional_accuracy: float
    source: str
