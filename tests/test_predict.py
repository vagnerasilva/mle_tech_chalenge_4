import datetime

from fastapi import status

from app.services import model_service
from ml.inference import ModelNotLoadedError


def _historical_points(n):
    base = datetime.date(2024, 1, 1)
    return [
        {"date": (base + datetime.timedelta(days=i)).isoformat(), "close": 2.5 + (i % 10) * 0.01}
        for i in range(n)
    ]


def test_predict_requires_symbol_or_historical_data(client):
    response = client.post("/api/v1/predict", json={"days_ahead": 1})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_predict_rejects_both_symbol_and_historical_data(client):
    response = client.post(
        "/api/v1/predict",
        json={"symbol": "BBD", "historical_data": _historical_points(35), "days_ahead": 1},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_predict_rejects_insufficient_historical_data(client):
    """sequence_length do modelo é 30 — enviar menos pontos deve falhar com 422, não 500."""
    response = client.post(
        "/api/v1/predict",
        json={"historical_data": _historical_points(5), "days_ahead": 1},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "sequence_length" in response.json()["detail"] or "necessário" in response.json()["detail"]


def test_predict_with_historical_data_returns_real_prediction(client):
    sequence_length = model_service.get_service().sequence_length
    response = client.post(
        "/api/v1/predict",
        json={"historical_data": _historical_points(sequence_length + 5), "days_ahead": 2},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["days_ahead"] == 2
    assert len(data["predictions"]) == 2
    assert isinstance(data["predicted_close"], float)
    assert data["model_version"]


def test_predict_returns_503_when_model_not_loaded(client, monkeypatch):
    class _NotLoadedService:
        def predict(self, **kwargs):
            raise ModelNotLoadedError("modelo não carregado")

    monkeypatch.setattr(model_service, "get_service", lambda: _NotLoadedService())

    response = client.post(
        "/api/v1/predict",
        json={"historical_data": _historical_points(35), "days_ahead": 1},
    )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_predict_with_symbol_fetches_live_data(client):
    """Teste de integração real: busca dados ao vivo via yfinance para o ticker
    oficial do projeto (BBD) e confirma que a predição não é mockada."""
    response = client.post("/api/v1/predict", json={"symbol": "BBD", "days_ahead": 1})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["symbol"] == "BBD"
    # BBD historicamente opera na faixa de USD 1 a 6 — checagem de sanidade,
    # não uma métrica de precisão do modelo.
    assert 0.5 < data["predicted_close"] < 20
