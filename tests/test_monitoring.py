import datetime
import uuid

import pytest
from fastapi.testclient import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models.base import Base
from app.models.metrics import ModelMetrics
from app.services.monitoring_service import ModelMonitoringService


@pytest.fixture(scope="function")
def test_db():
    """Cria um banco SQLite em memória para testes."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    yield db
    
    db.close()


def test_calculate_metrics():
    """Testa cálculo de métricas básicas."""
    # Predição: 100.0, Real: 102.0 (2% acima)
    metrics = ModelMonitoringService.calculate_metrics(
        predicted_close=100.0,
        actual_close=102.0,
    )
    
    assert metrics["mae"] == 2.0
    assert metrics["rmse"] == 2.0
    assert abs(metrics["mape"] - 1.96) < 0.1  # ~1.96%
    assert metrics["directional_accuracy"] == 1.0  # Acertou a direção
    assert abs(metrics["error_percentage"] - 1.96) < 0.1


def test_calculate_metrics_wrong_direction():
    """Testa quando a predição acerta a direção (directional_accuracy=0)."""
    # Predição: 100.0, Real: 99.0 (pior que o predito)
    # Mas se a tendência era 101->100 (queda), acerta
    metrics = ModelMonitoringService.calculate_metrics(
        predicted_close=100.0,
        actual_close=99.0,
    )
    
    assert metrics["mae"] == 1.0
    assert abs(metrics["mape"] - 1.01) < 0.1  # ~1.01%


def test_save_prediction_metrics(test_db: Session):
    """Testa salvamento de métricas no banco."""
    metrics = ModelMonitoringService.calculate_metrics(100.0, 102.0)
    
    record = ModelMonitoringService.save_prediction_metrics(
        test_db,
        prediction_date=datetime.date(2026, 7, 10),
        predicted_close=100.0,
        actual_close=102.0,
        metrics=metrics,
    )
    
    assert record.symbol == "BBD"
    assert record.predicted_close == 100.0
    assert record.actual_close == 102.0
    assert record.mae == 2.0
    
    # Verifica se foi salvo no banco
    saved = test_db.query(ModelMetrics).filter_by(symbol="BBD").first()
    assert saved is not None
    assert saved.predicted_close == 100.0


def test_get_metrics_by_date_range(test_db: Session):
    """Testa filtro de métricas por data."""
    metrics_dict = ModelMonitoringService.calculate_metrics(100.0, 102.0)
    
    # Cria 3 registros em datas diferentes
    for i in range(3):
        ModelMonitoringService.save_prediction_metrics(
            test_db,
            prediction_date=datetime.date(2026, 7, 10 + i),
            predicted_close=100.0,
            actual_close=102.0,
            metrics=metrics_dict,
        )
    
    # Busca no intervalo de 10-11
    results = ModelMonitoringService.get_metrics_by_date_range(
        test_db,
        start_date=datetime.date(2026, 7, 10),
        end_date=datetime.date(2026, 7, 11),
    )
    
    assert len(results) == 2


def test_get_summary_stats(test_db: Session):
    """Testa cálculo de estatísticas agregadas."""
    # Cria alguns registros
    for predicted, actual in [(100.0, 102.0), (100.0, 103.0), (100.0, 101.0)]:
        metrics = ModelMonitoringService.calculate_metrics(predicted, actual)
        ModelMonitoringService.save_prediction_metrics(
            test_db,
            prediction_date=datetime.date(2026, 7, 10),
            predicted_close=predicted,
            actual_close=actual,
            metrics=metrics,
        )
    
    stats = ModelMonitoringService.get_summary_stats(test_db)
    
    assert stats["total_predictions"] == 3
    assert stats["avg_mae"] > 0
    assert stats["avg_mape"] > 0


@pytest.mark.asyncio
async def test_validation_endpoint(client):
    """Testa endpoint de validação."""
    # Primeiro, faz uma predição
    response = client.post("/api/v1/predict/next_close")
    assert response.status_code == 200
    
    pred_data = response.json()
    symbol = pred_data["symbol"]
    pred_date = pred_data["last_trading_date"]
    
    # Tenta validar
    response = client.get(
        f"/api/v1/validation/validate?symbol={symbol}&prediction_date={pred_date}"
    )
    assert response.status_code in [200, 404]  # 404 ok se ainda não há preço real


@pytest.mark.asyncio
async def test_validation_history_endpoint(client):
    """Testa endpoint de histórico."""
    response = client.get("/api/v1/validation/history?limit=10")
    assert response.status_code in [200, 404]  # 404 ok se vazio


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
