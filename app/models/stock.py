from pydantic import BaseModel, Field


class DataCollectRequest(BaseModel):
    symbol: str = Field(..., description="Ticker, ex.: BBD, AAPL, PETR4.SA")
    start_date: str = Field(..., description="Data inicial YYYY-MM-DD")
    end_date: str = Field(..., description="Data final YYYY-MM-DD")


class DataCollectResponse(BaseModel):
    symbol: str
    start_date: str
    end_date: str
    rows_collected: int
    file_path: str
    columns: list[str]


class TrainRequest(BaseModel):
    symbol: str = Field(..., description="Ticker a treinar")
    start_date: str
    end_date: str
    sequence_length: int = Field(30, ge=5, le=250)
    epochs: int = Field(50, ge=1, le=1000)
    batch_size: int = Field(32, ge=1, le=512)


class TrainResponse(BaseModel):
    model_name: str
    model_version: str
    symbol: str
    sequence_length: int
    metrics: dict
    trained_at: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str | None
    current_time: str
    environment: str


class ModelInfoResponse(BaseModel):
    model_name: str
    model_type: str
    symbol: str
    data_start_date: str
    data_end_date: str
    sequence_length: int
    features: list[str]
    metrics: dict
    trained_at: str
    model_path: str
    model_version: str


class MetricsResponse(BaseModel):
    mae: float
    rmse: float
    mape: float
    directional_accuracy: float | None = None
    final_loss: float | None = None
    final_val_loss: float | None = None
    trained_at: str
    dataset_size: int


class MonitoringResponse(BaseModel):
    total_calls: int
    avg_response_time_ms: float | None
    status_counts: dict
    recent_predictions: list[dict]
    api_status: str
