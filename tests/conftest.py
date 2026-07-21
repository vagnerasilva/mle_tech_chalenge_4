import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.dependencies import get_db
from app.main import app
from app.models.base import Base
from app.schemas.predict import (
    BatchPredictItem,
    BatchPredictResponse,
    PredictResponse,
    SequencePredictResponse,
)
from app.services.prediction_service import get_prediction_service


class FakePredictionService:
    """Substitui o modelo LSTM real + chamadas ao yfinance por valores determinísticos."""

    def predict_single(self, symbol: str) -> PredictResponse:
        return PredictResponse(
            symbol=symbol,
            predicted_close=42.0,
            last_trading_date=datetime.date(2026, 7, 10),
            look_back=30,
        )

    def predict_batch(self, symbols: list[str]) -> BatchPredictResponse:
        results = {
            symbol: BatchPredictItem(predicted_close=42.0, last_trading_date=datetime.date(2026, 7, 10))
            for symbol in symbols
        }
        return BatchPredictResponse(results=results, generated_at=datetime.datetime(2026, 7, 13, 12, 0, 0))

    def predict_sequence(self, symbol: str, days_ahead: int) -> SequencePredictResponse:
        return SequencePredictResponse(symbol=symbol, days_ahead=days_ahead, predictions=[42.0] * days_ahead)


@pytest.fixture
def test_db():
    """Banco SQLite em memória — isola os testes do data/database.db real."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    app.dependency_overrides[get_prediction_service] = lambda: FakePredictionService()
    app.dependency_overrides[get_db] = lambda: test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
