def test_predict_single_returns_prediction(client):
    response = client.post("/api/v1/predict/single", json={"symbol": "PETR4.SA"})

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "PETR4.SA"
    assert body["predicted_close"] == 42.0
    assert body["look_back"] == 30


def test_predict_single_requires_symbol(client):
    response = client.post("/api/v1/predict/single", json={})

    assert response.status_code == 422


def test_predict_batch_returns_one_result_per_symbol(client):
    response = client.post(
        "/api/v1/predict/batch", json={"symbols": ["PETR4.SA", "VALE3.SA"]}
    )

    assert response.status_code == 200
    results = response.json()["results"]
    assert set(results.keys()) == {"PETR4.SA", "VALE3.SA"}
    assert results["PETR4.SA"]["predicted_close"] == 42.0


def test_predict_sequence_returns_days_ahead_predictions(client):
    response = client.post(
        "/api/v1/predict/sequence", json={"symbol": "PETR4.SA", "days_ahead": 5}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["days_ahead"] == 5
    assert len(body["predictions"]) == 5


def test_predict_sequence_rejects_invalid_days_ahead(client):
    response = client.post(
        "/api/v1/predict/sequence", json={"symbol": "PETR4.SA", "days_ahead": 0}
    )

    assert response.status_code == 422


def test_metrics_latest(client):
    response = client.get("/api/v1/metrics/latest")

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "BBD"
    assert 0 < body["mape"] < 100
