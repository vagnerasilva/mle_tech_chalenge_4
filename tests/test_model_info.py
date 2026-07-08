from fastapi import status

from app.services import model_service


def test_model_info_returns_metadata(client):
    response = client.get("/api/v1/model/info")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["model_type"] == "LSTM"
    assert data["symbol"]
    assert data["sequence_length"] > 0
    assert isinstance(data["features"], list)
    assert "mae" in data["metrics"]


def test_model_metrics_returns_evaluation_numbers(client):
    response = client.get("/api/v1/model/metrics")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data["mae"], float)
    assert isinstance(data["rmse"], float)
    assert isinstance(data["mape"], float)


def test_model_info_returns_503_when_model_not_loaded(client, monkeypatch):
    class _NotLoadedService:
        loaded = False
        metadata = {}
        model_version = None
        symbol = ""

    monkeypatch.setattr(model_service, "get_service", lambda: _NotLoadedService())

    response = client.get("/api/v1/model/info")

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
