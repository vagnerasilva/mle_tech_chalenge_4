def test_health_reports_model_loaded(client):
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True


def test_readiness_ok_when_artifacts_present(client):
    response = client.get("/readiness")

    assert response.status_code == 200
    assert response.json() == {"ready": True, "detail": None}
