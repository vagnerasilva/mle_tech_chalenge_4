import datetime

from pydantic import BaseModel, ConfigDict, Field


class MetricRecordResponse(BaseModel):
    """Resposta com um registro de métrica individual."""
    
    id: str
    symbol: str
    prediction_date: datetime.date
    actual_date: datetime.date
    
    predicted_close: float = Field(..., description="Preço predito pelo modelo")
    actual_close: float | None = Field(None, description="Preço real do ativo")
    
    mae: float | None = Field(None, description="Mean Absolute Error")
    rmse: float | None = Field(None, description="Root Mean Squared Error")
    mape: float | None = Field(None, description="Mean Absolute Percentage Error (%)")
    directional_accuracy: float | None = Field(None, description="1.0 se direção correta, 0.0 se não")
    error_percentage: float | None = Field(None, description="Erro percentual (%)")
    
    created_at: datetime.datetime
    
    model_config = ConfigDict(from_attributes=True)


class ValidationResponse(BaseModel):
    """Resposta com resultados de validação (predições vs valores reais)."""
    
    symbol: str
    prediction_date: datetime.date
    predicted_close: float
    actual_close: float | None
    mae: float | None
    mape: float | None
    directional_accuracy: float | None
    error_percentage: float | None
    status: str = Field(..., description="'validated' se preço real encontrado, 'pending' se não")


class ValidationSummaryResponse(BaseModel):
    """Resumo de validações para um período."""
    
    symbol: str
    start_date: datetime.date
    end_date: datetime.date
    total_predictions: int
    validated: int = Field(..., description="Quantas têm preço real")
    pending: int = Field(..., description="Quantas ainda não têm preço real")
    
    avg_mae: float | None
    avg_rmse: float | None
    avg_mape: float | None
    avg_directional_accuracy: float | None
    
    min_mae: float | None
    max_mae: float | None
    min_mape: float | None
    max_mape: float | None


class ModelSummaryStatsResponse(BaseModel):
    """Estatísticas agregadas do desempenho do modelo."""
    
    total_predictions: int
    avg_mae: float
    avg_rmse: float
    avg_mape: float
    avg_directional_accuracy: float
    min_mae: float
    max_mae: float
    min_mape: float
    max_mape: float
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "total_predictions": 45,
                    "avg_mae": 0.1234,
                    "avg_rmse": 0.1456,
                    "avg_mape": 3.45,
                    "avg_directional_accuracy": 0.67,
                    "min_mae": 0.01,
                    "max_mae": 0.45,
                    "min_mape": 0.5,
                    "max_mape": 12.3,
                }
            ]
        }
    )


class PendingValidationResponse(BaseModel):
    """Resposta da validação automática de predições pendentes."""
    
    total_pending: int = Field(..., description="Total de predições pendentes encontradas")
    updated: int = Field(..., description="Quantas foram atualizadas com sucesso")
    pending: int = Field(..., description="Quantas ainda não têm preço real após essa tentativa")
    failed: int = Field(..., description="Quantas falharam por erro de execução durante a validação")
    updated_records: list[MetricRecordResponse] = Field(..., description="Detalhes dos registros atualizados")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "total_pending": 5,
                    "updated": 4,
                    "pending": 1,
                    "failed": 0,
                    "updated_records": []
                }
            ]
        }
    )


class MetricsAverageResponse(BaseModel):
    """Médias das métricas presentes no banco de dados."""
    
    total_validated: int = Field(..., description="Total de predições validadas")
    total_pending: int = Field(..., description="Total de predições ainda pendentes")
    
    avg_mae: float | None = Field(None, description="Média do Mean Absolute Error")
    avg_rmse: float | None = Field(None, description="Média do Root Mean Squared Error")
    avg_mape: float | None = Field(None, description="Média do Mean Absolute Percentage Error (%)")
    avg_directional_accuracy: float | None = Field(None, description="Média de Acurácia Direcional")
    avg_error_percentage: float | None = Field(None, description="Média do Erro Percentual (%)")
    
    min_mae: float | None = Field(None, description="Mínimo MAE")
    max_mae: float | None = Field(None, description="Máximo MAE")
    min_mape: float | None = Field(None, description="Mínimo MAPE")
    max_mape: float | None = Field(None, description="Máximo MAPE")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "total_validated": 40,
                    "total_pending": 2,
                    "avg_mae": 0.0856,
                    "avg_rmse": 0.1023,
                    "avg_mape": 2.43,
                    "avg_directional_accuracy": 0.72,
                    "avg_error_percentage": 1.56,
                    "min_mae": 0.001,
                    "max_mae": 0.456,
                    "min_mape": 0.03,
                    "max_mape": 8.92,
                }
            ]
        }
    )
