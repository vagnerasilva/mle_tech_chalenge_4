from fastapi import status


def test_ml_features_returns_sample_and_metadata(client):
    response = client.get("/api/v1/ml/features")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "features" in data
    assert "sequence_length" in data
    assert isinstance(data["sample_processed"], list)


def test_monitoring_metrics_tracks_calls(client):
    # Gera pelo menos uma chamada registrada antes de consultar o monitoramento
    client.get("/api/v1/health")

    response = client.get("/api/v1/monitoring/metrics")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_calls"] >= 0
    assert "status_counts" in data
    assert "recent_predictions" in data
