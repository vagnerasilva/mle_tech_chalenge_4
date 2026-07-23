import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import numpy as np

from app.core.config import Settings, get_settings
from app.dependencies import get_db
from app.schemas.monitoring import (
    MetricRecordResponse,
    MetricsAverageResponse,
    ModelSummaryStatsResponse,
    PendingValidationResponse,
    ValidationResponse,
    ValidationSummaryResponse,
)
from app.services.monitoring_service import ModelMonitoringService

router = APIRouter(prefix="/validation", tags=["validation"])



@router.post(
    "/validate",
    response_model=PendingValidationResponse,
    summary="Valida todas as predições pendentes",
    description="Percorre todas as predições que ainda não têm preço real, tenta buscar do yfinance e atualiza as que conseguir encontrar.",
)
def validate_all_pending(
    db: Session = Depends(get_db),
) -> PendingValidationResponse:
    """
    Valida automaticamente todas as predições pendentes.
    
    - Busca todas as predições com actual_close = NULL
    - Para cada uma, tenta obter o preço real do yfinance
    - Se encontra: calcula métricas e atualiza o registro
    - Se não encontra: deixa pendente para tentar depois
    - Retorna resumo com quantas foram atualizadas
    
    Exemplo:
    ```
    POST /api/v1/validation/validate
    ```
    """
    from app.models.metrics import ModelMetrics

    # Função para verificar se é fim de semana (sábado ou domingo)
    def is_weekend(prediction_date):
        # prediction_date é um objeto date, weekday() retorna: 0=seg, 5=sab, 6=dom
        day_of_week = prediction_date.weekday()
        return day_of_week in [5, 6]  # sábado (5), domingo (6)

    # Busca todos os registros pendentes ou sem métricas calculadas
    all_pending_records = (
        db.query(ModelMetrics)
        .filter(
            (ModelMetrics.actual_close == None) |
            (ModelMetrics.mae == None) |
            (ModelMetrics.rmse == None) |
            (ModelMetrics.mape == None) |
            (ModelMetrics.directional_accuracy == None) |
            (ModelMetrics.error_percentage == None)
        )
        .all()
    )

    # Filtrar apenas os registros que NÃO são de fim de semana
    pending_records = [r for r in all_pending_records if not is_weekend(r.prediction_date)]
    fds_count = len(all_pending_records) - len(pending_records)

    updated_records = []
    pending_count = 0
    failed_count = 0

    for record in pending_records:
        try:
            # Tenta buscar o preço real
            actual_price = ModelMonitoringService.get_actual_price(
                record.prediction_date,
            )
            
            if actual_price is not None:
                # Calcula métricas
                metrics = ModelMonitoringService.calculate_metrics(
                    record.predicted_close,
                    actual_price,
                )
                
                # Atualiza o registro
                record.actual_close = actual_price
                record.mae = metrics["mae"]
                record.rmse = metrics["rmse"]
                record.mape = metrics["mape"]
                record.directional_accuracy = metrics["directional_accuracy"]
                record.error_percentage = metrics["error_percentage"]
                record.updated_at = datetime.datetime.utcnow()
                
                updated_records.append(MetricRecordResponse.model_validate(record))
            else:
                pending_count += 1
                
        except Exception as e:
            print(f"Erro ao validar predição {record.symbol} em {record.prediction_date}: {e}")
            failed_count += 1
    
    # Commit de todos os registros atualizados
    db.commit()

    return PendingValidationResponse(
        total_pending=len(pending_records),
        updated=len(updated_records),
        pending=pending_count,
        failed=failed_count,
        skipped_fds=fds_count,
        updated_records=updated_records,
    )


@router.get(
    "/get-metrics",
    response_model=MetricsAverageResponse,
    summary="Retorna as médias de todas as métricas",
    description="Calcula e retorna as médias de mae, rmse, mape, directional_accuracy de todos os registros validados no banco.",
)
def get_metrics_average(
    db: Session = Depends(get_db),
) -> MetricsAverageResponse:
    """
    Retorna as médias agregadas de todas as métricas presentes no banco.
    
    - Separa registros validados vs pendentes
    - Calcula médias de mae, rmse, mape, directional_accuracy
    - Retorna também mínimos e máximos
    
    Exemplo:
    ```
    GET /api/v1/validation/get-metrics
    ```
    """
    from app.models.metrics import ModelMetrics
    
    # Busca todos os registros
    all_records = db.query(ModelMetrics).all()
    
    # Separa validados e pendentes
    validated = [r for r in all_records if r.actual_close is not None]
    pending = [r for r in all_records if r.actual_close is None]
    
    # Extrai valores
    mae_values = [r.mae for r in validated if r.mae is not None]
    rmse_values = [r.rmse for r in validated if r.rmse is not None]
    mape_values = [r.mape for r in validated if r.mape is not None]
    dir_acc_values = [r.directional_accuracy for r in validated if r.directional_accuracy is not None]
    error_pct_values = [r.error_percentage for r in validated if r.error_percentage is not None]
    
    # Calcula médias e extremos
    return MetricsAverageResponse(
        total_validated=len(validated),
        total_pending=len(pending),
        avg_mae=float(np.mean(mae_values)) if mae_values else None,
        avg_rmse=float(np.mean(rmse_values)) if rmse_values else None,
        avg_mape=float(np.mean(mape_values)) if mape_values else None,
        avg_directional_accuracy=float(np.mean(dir_acc_values)) if dir_acc_values else None,
        avg_error_percentage=float(np.mean(error_pct_values)) if error_pct_values else None,
        min_mae=float(np.min(mae_values)) if mae_values else None,
        max_mae=float(np.max(mae_values)) if mae_values else None,
        min_mape=float(np.min(mape_values)) if mape_values else None,
        max_mape=float(np.max(mape_values)) if mape_values else None,
    )


@router.get(
    "/history",
    response_model=list[MetricRecordResponse],
    summary="Lista histórico de predições validadas",
    description="Retorna todas as predições registradas para BBD, filtradas opcionalmente por intervalo de datas.",
)
def get_validation_history(
    start_date: datetime.date | None = Query(None, description="Data inicial (inclusive)"),
    end_date: datetime.date | None = Query(None, description="Data final (inclusive)"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de registros a retornar"),
    db: Session = Depends(get_db),
) -> list[MetricRecordResponse]:
    """
    Retorna o histórico de predições com suas métricas para BBD.
    
    Permite filtrar por:
    - `start_date`, `end_date`: Intervalo de datas
    - `limit`: Quantidade máxima de registros (padrão 100)
    
    Exemplo:
    ```
    GET /api/v1/validation/history?start_date=2026-06-01&limit=50
    ```
    """
    records = ModelMonitoringService.get_metrics_by_date_range(
        db,
        start_date=start_date,
        end_date=end_date,
    )
    
    return [MetricRecordResponse.model_validate(r) for r in records[:limit]]


@router.get(
    "/summary",
    response_model=ValidationSummaryResponse,
    summary="Resumo de validações num período",
    description="Calcula estatísticas agregadas para BBD num período específico.",
)
def get_validation_summary(
    start_date: datetime.date | None = Query(None, description="Data inicial (padrão: últimos 30 dias)"),
    end_date: datetime.date | None = Query(None, description="Data final (padrão: hoje)"),
    db: Session = Depends(get_db),
) -> ValidationSummaryResponse:
    """
    Retorna um resumo de validações para BBD num intervalo de datas.
    
    Calcula:
    - Total de predições
    - Quantas foram validadas vs pendentes
    - Médias de mae, rmse, mape, directional_accuracy
    - Mínimos e máximos
    
    Exemplo:
    ```
    GET /api/v1/validation/summary?start_date=2026-06-01&end_date=2026-07-15
    ```
    """
    from app.models.metrics import ModelMetrics
    
    SYMBOL = "BBD"
    
    # Padrões de data
    if end_date is None:
        end_date = datetime.date.today()
    if start_date is None:
        start_date = end_date - datetime.timedelta(days=30)
    
    # Busca registros
    records = ModelMonitoringService.get_metrics_by_date_range(
        db,
        start_date=start_date,
        end_date=end_date,
    )
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nenhuma predição encontrada para {SYMBOL} entre {start_date} e {end_date}",
        )
    
    validated = [r for r in records if r.actual_close is not None]
    pending = [r for r in records if r.actual_close is None]
    
    # Calcula médias apenas dos registros validados
    mae_values = [r.mae for r in validated if r.mae is not None]
    rmse_values = [r.rmse for r in validated if r.rmse is not None]
    mape_values = [r.mape for r in validated if r.mape is not None]
    dir_acc_values = [r.directional_accuracy for r in validated if r.directional_accuracy is not None]
    
    return ValidationSummaryResponse(
        symbol=SYMBOL,
        start_date=start_date,
        end_date=end_date,
        total_predictions=len(records),
        validated=len(validated),
        pending=len(pending),
        avg_mae=float(np.mean(mae_values)) if mae_values else None,
        avg_rmse=float(np.mean(rmse_values)) if rmse_values else None,
        avg_mape=float(np.mean(mape_values)) if mape_values else None,
        avg_directional_accuracy=float(np.mean(dir_acc_values)) if dir_acc_values else None,
        min_mae=float(np.min(mae_values)) if mae_values else None,
        max_mae=float(np.max(mae_values)) if mae_values else None,
        min_mape=float(np.min(mape_values)) if mape_values else None,
        max_mape=float(np.max(mape_values)) if mape_values else None,
    )


@router.get(
    "/stats",
    response_model=ModelSummaryStatsResponse,
    summary="Estatísticas gerais do modelo",
    description="Retorna agregações de todas as predições validadas para BBD.",
)
def get_model_stats(
    db: Session = Depends(get_db),
) -> ModelSummaryStatsResponse:
    """
    Retorna estatísticas agregadas do desempenho do modelo para BBD.
    
    Exemplo:
    ```
    GET /api/v1/validation/stats
    ```
    """
    stats = ModelMonitoringService.get_summary_stats(db)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma métrica encontrada para BBD",
        )
    
    return ModelSummaryStatsResponse(**stats)
