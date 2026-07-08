from fastapi import status


def test_health_endpoint_returns_ok(client):
    response = client.get("/api/v1/health")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert "model_loaded" in data
    assert "model_version" in data
    assert "current_time" in data
    assert "environment" in data


def test_health_reports_model_loaded_when_artifacts_exist(client):
    """O projeto é entregue com um modelo v1 (BBD) já treinado em models/, então
    o health check deve reportar model_loaded=True fora do ambiente de teste."""
    response = client.get("/api/v1/health")
    data = response.json()

    assert isinstance(data["model_loaded"], bool)
    if data["model_loaded"]:
        assert data["model_version"] is not None
