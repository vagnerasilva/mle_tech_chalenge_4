from fastapi import status


def test_collect_rejects_invalid_dates(client):
    response = client.post(
        "/api/v1/data/collect",
        json={"symbol": "BBD", "start_date": "not-a-date", "end_date": "2024-07-20"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_collect_rejects_start_after_end(client):
    response = client.post(
        "/api/v1/data/collect",
        json={"symbol": "BBD", "start_date": "2024-07-20", "end_date": "2024-01-01"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_collect_rejects_invalid_ticker(client):
    response = client.post(
        "/api/v1/data/collect",
        json={"symbol": "ZZZZINVALIDTICKER123", "start_date": "2024-01-01", "end_date": "2024-02-01"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_collect_valid_symbol_returns_summary(client):
    response = client.post(
        "/api/v1/data/collect",
        json={"symbol": "BBD", "start_date": "2024-01-01", "end_date": "2024-02-01"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["symbol"] == "BBD"
    assert data["rows_collected"] > 0
    assert "Close" in data["columns"]
