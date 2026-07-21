"""
🔍 Testes do Sistema de Validação e Monitoramento de Desempenho

Testa:
- Cálculo de métricas (MAE, RMSE, MAPE, directional_accuracy)
- Validação de predições pendentes
- Busca de resumos de validação
- Estatísticas agregadas do modelo
"""

import datetime
import uuid
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.models.metrics import ModelMetrics
from app.services.monitoring_service import ModelMonitoringService


class TestModelMonitoringService:
    """Testes do serviço de monitoramento de desempenho."""

    def test_calculate_metrics_perfect_prediction(self):
        """Predição perfeita deve resultar em erro zero."""
        metrics = ModelMonitoringService.calculate_metrics(
            predicted_close=25.50,
            actual_close=25.50,
        )

        assert metrics["mae"] == 0.0
        assert metrics["rmse"] == 0.0
        assert metrics["mape"] == 0.0
        assert metrics["error_percentage"] == 0.0

    def test_calculate_metrics_positive_error(self):
        """Predição menor que o real (subestimou)."""
        metrics = ModelMonitoringService.calculate_metrics(
            predicted_close=25.00,
            actual_close=26.00,
        )

        assert metrics["mae"] == 1.0  # |26 - 25| = 1
        assert metrics["rmse"] > 0
        assert metrics["mape"] > 0
        assert metrics["error_percentage"] < 0  # Erro negativo (subestimou)

    def test_calculate_metrics_negative_error(self):
        """Predição maior que o real (superestimou)."""
        metrics = ModelMonitoringService.calculate_metrics(
            predicted_close=27.00,
            actual_close=26.00,
        )

        assert metrics["mae"] == 1.0  # |26 - 27| = 1
        assert metrics["error_percentage"] > 0  # Erro positivo (superestimou)

    def test_calculate_metrics_mape_calculation(self):
        """Verificar cálculo correto do MAPE."""
        # Predição: 25.00, Valor real: 25.50
        # MAPE = |25.50 - 25.00| / 25.50 * 100 = 1.96%
        metrics = ModelMonitoringService.calculate_metrics(
            predicted_close=25.00,
            actual_close=25.50,
        )

        expected_mape = (0.50 / 25.50) * 100
        assert abs(metrics["mape"] - expected_mape) < 0.01

    def test_calculate_metrics_directional_accuracy_up(self):
        """Acurácia direcional: se predição >= real e real > predicted."""
        # Predição subestimou (25 < 26)
        # Direção: real > predicted = subestimou (movimento para cima)
        metrics = ModelMonitoringService.calculate_metrics(
            predicted_close=25.00,
            actual_close=26.00,
        )

        # Verificar que directional_accuracy é calculado
        assert "directional_accuracy" in metrics
        assert metrics["directional_accuracy"] in [0.0, 1.0]

    def test_calculate_metrics_zero_actual_close(self):
        """Proteção contra divisão por zero quando actual_close = 0."""
        metrics = ModelMonitoringService.calculate_metrics(
            predicted_close=25.00,
            actual_close=0.0,
        )

        assert metrics["mape"] == 0.0
        assert metrics["error_percentage"] == 0.0
        assert metrics["mae"] == 25.0

    def test_save_prediction_metrics(self, db_session: Session):
        """Teste de salvamento de métricas no banco."""
        prediction_date = datetime.date.today()
        actual_date = datetime.date.today()
        metrics = {
            "mae": 0.12,
            "rmse": 0.15,
            "mape": 2.3,
            "directional_accuracy": 0.67,
            "error_percentage": -1.5,
        }

        result = ModelMonitoringService.save_prediction_metrics(
            db=db_session,
            prediction_date=prediction_date,
            predicted_close=25.34,
            actual_close=25.66,
            metrics=metrics,
        )

        assert isinstance(result, ModelMetrics)
        assert result.symbol == "BBD"
        assert result.predicted_close == 25.34
        assert result.actual_close == 25.66
        assert result.mae == 0.12
        assert result.mape == 2.3

    @patch("yfinance.download")
    def test_get_actual_price_success(self, mock_yf):
        """Buscar preço real com sucesso via yfinance."""
        import pandas as pd

        mock_df = pd.DataFrame({
            "Close": [25.50],
        }, index=pd.DatetimeIndex([datetime.date.today()]))

        mock_yf.return_value = mock_df

        actual_price = ModelMonitoringService.get_actual_price(
            datetime.date.today()
        )

        assert actual_price is not None
        assert actual_price == 25.50

    @patch("yfinance.download")
    def test_get_actual_price_not_found(self, mock_yf):
        """Quando preço real não está disponível."""
        mock_yf.return_value = None

        actual_price = ModelMonitoringService.get_actual_price(
            datetime.date.today()
        )

        assert actual_price is None

    def test_metrics_all_fields_present(self):
        """Verificar que todas as métricas esperadas são retornadas."""
        metrics = ModelMonitoringService.calculate_metrics(25.0, 26.0)

        expected_fields = [
            "mae",
            "rmse",
            "mape",
            "directional_accuracy",
            "error_percentage",
        ]

        for field in expected_fields:
            assert field in metrics, f"Campo {field} faltando nas métricas"

    def test_metrics_are_floats(self):
        """Todas as métricas devem ser floats."""
        metrics = ModelMonitoringService.calculate_metrics(25.0, 26.0)

        for key, value in metrics.items():
            assert isinstance(value, float), f"{key} não é float: {type(value)}"


class TestMetricsStorage:
    """Testes de armazenamento de métricas no banco."""

    def test_model_metrics_table_schema(self, db_session: Session):
        """Verificar que a tabela model_metrics foi criada corretamente."""
        from app.models.base import Base, engine

        # Criar tabelas
        Base.metadata.create_all(bind=engine)

        # Verificar que tabela existe
        inspector = __import__("sqlalchemy").inspect(engine)
        assert "model_metrics" in inspector.get_table_names()

    def test_save_multiple_metrics(self, db_session: Session):
        """Salvar múltiplas métricas para o mesmo símbolo."""
        metrics = {
            "mae": 0.12,
            "rmse": 0.15,
            "mape": 2.3,
            "directional_accuracy": 0.67,
            "error_percentage": -1.5,
        }

        for i in range(5):
            ModelMonitoringService.save_prediction_metrics(
                db=db_session,
                prediction_date=datetime.date.today() - datetime.timedelta(days=i),
                predicted_close=25.0 + i * 0.1,
                actual_close=25.5 + i * 0.1,
                metrics=metrics,
            )

        # Verificar quantidade
        from sqlalchemy import func

        count = db_session.query(func.count(ModelMetrics.id)).scalar()
        assert count == 5

    def test_metrics_with_null_actual_close(self, db_session: Session):
        """Salvar métrica com actual_close = NULL (predição pendente)."""
        db_session.add(ModelMetrics(
            id=str(uuid.uuid4()),
            symbol="BBD",
            prediction_date=datetime.date.today(),
            actual_date=None,
            predicted_close=25.34,
            actual_close=None,  # Pendente
            mae=None,
            rmse=None,
            mape=None,
            directional_accuracy=None,
            error_percentage=None,
        ))
        db_session.commit()

        # Verificar que foi salvo
        record = db_session.query(ModelMetrics).filter(
            ModelMetrics.predicted_close == 25.34
        ).first()

        assert record is not None
        assert record.actual_close is None
        assert record.mae is None


class TestValidationResponse:
    """Testes de schemas de resposta de validação."""

    def test_metric_record_response_schema(self):
        """Validar schema de resposta de um registro de métrica."""
        from app.schemas.monitoring import MetricRecordResponse

        response = MetricRecordResponse(
            id="test-id",
            symbol="BBD",
            prediction_date=datetime.date.today(),
            actual_date=datetime.date.today(),
            predicted_close=25.34,
            actual_close=25.66,
            mae=0.12,
            rmse=0.15,
            mape=2.3,
            directional_accuracy=0.67,
            error_percentage=-1.5,
            created_at=datetime.datetime.now(),
        )

        assert response.symbol == "BBD"
        assert response.predicted_close == 25.34
        assert response.mape == 2.3

    def test_validation_summary_response_schema(self):
        """Validar schema de resumo de validações."""
        from app.schemas.monitoring import ValidationSummaryResponse

        response = ValidationSummaryResponse(
            symbol="BBD",
            start_date=datetime.date(2026, 7, 1),
            end_date=datetime.date(2026, 7, 14),
            total_predictions=50,
            validated=48,
            pending=2,
            avg_mae=0.12,
            avg_rmse=0.15,
            avg_mape=2.3,
            avg_directional_accuracy=0.67,
            min_mae=0.01,
            max_mae=0.45,
            min_mape=0.5,
            max_mape=12.3,
        )

        assert response.total_predictions == 50
        assert response.validated == 48
        assert response.avg_mape == 2.3

    def test_model_summary_stats_response_schema(self):
        """Validar schema de estatísticas agregadas."""
        from app.schemas.monitoring import ModelSummaryStatsResponse

        response = ModelSummaryStatsResponse(
            total_predictions=150,
            avg_mae=0.15,
            avg_rmse=0.18,
            avg_mape=2.8,
            avg_directional_accuracy=0.65,
            min_mae=0.01,
            max_mae=0.50,
            min_mape=0.3,
            max_mape=15.0,
        )

        assert response.total_predictions == 150
        assert response.avg_mae == 0.15


class TestValidationEndpoints:
    """Testes de endpoints de validação."""

    @pytest.mark.asyncio
    async def test_validate_all_pending_endpoint(self, client, db_session):
        """Teste do endpoint POST /api/v1/validation/validate."""
        # Isso seria um teste de integração que requer um cliente FastAPI
        # Deixamos a estrutura para futuras implementações
        pass

    @pytest.mark.asyncio
    async def test_get_validation_summary_endpoint(self, client):
        """Teste do endpoint GET /api/v1/validation/summary."""
        pass

    @pytest.mark.asyncio
    async def test_get_model_summary_stats_endpoint(self, client):
        """Teste do endpoint GET /api/v1/validation/metrics."""
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
