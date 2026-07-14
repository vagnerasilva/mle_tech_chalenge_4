import json
from datetime import datetime

from starlette.requests import Request
from starlette.responses import StreamingResponse

from app.models.logs import ApiLog
from app.services import log_service


def make_request(overrides=None):
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/predict/single",
        "headers": [(b"content-type", b"application/json")],
        "client": ("127.0.0.1", 12345),
        "query_string": b"",
        "root_path": "",
        "scheme": "http",
    }
    if overrides:
        scope.update(overrides)
    return Request(scope)


def test_api_log_model_persistence(test_db):
    """Verifica que um ApiLog é persistido corretamente na tabela api_logs."""
    log_entry = ApiLog(
        ip_address="127.0.0.1",
        path="/api/v1/predict/single",
        method="POST",
        status_code=200,
        process_time=0.5,
    )

    test_db.add(log_entry)
    test_db.commit()
    test_db.refresh(log_entry)

    assert log_entry.id is not None
    assert isinstance(log_entry.created_at, datetime)
    assert log_entry.ip_address == "127.0.0.1"
    assert log_entry.method == "POST"
    assert log_entry.status_code == 200


def test_write_log_creates_entry(test_db, monkeypatch):
    """Chama write_log diretamente e confirma que grava no banco."""
    from sqlalchemy.orm import sessionmaker

    service_db = sessionmaker(bind=test_db.bind)()
    monkeypatch.setattr(log_service, "get_db", lambda: iter([service_db]))

    req = make_request({"client": ("10.0.0.1", 54321), "path": "/api/v1/predict/batch", "method": "POST"})
    res = StreamingResponse(content=b'{"result": true}', media_type="application/json", status_code=201)

    log_service.write_log(req, res, process_time=0.123)

    logs = test_db.query(ApiLog).all()
    assert len(logs) == 1
    entry = logs[0]
    assert entry.path == "/api/v1/predict/batch"
    assert entry.method == "POST"
    assert entry.status_code == 201
    assert entry.ip_address == "10.0.0.1"

    service_db.close()


def test_list_logs_endpoint_returns_seeded_entries(client, test_db):
    """GET /api/v1/logs retorna os logs previamente gravados na tabela."""
    log_entry = ApiLog(
        ip_address="1.2.3.4",
        path="/api/v1/predict/single",
        method="POST",
        status_code=200,
        process_time=0.01,
    )
    test_db.add(log_entry)
    test_db.commit()

    response = client.get("/api/v1/logs")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(item["path"] == "/api/v1/predict/single" and item["method"] == "POST" for item in data)


def test_list_logs_endpoint_respects_limit(client, test_db):
    for i in range(3):
        test_db.add(ApiLog(ip_address="1.2.3.4", path=f"/x/{i}", method="GET", status_code=200, process_time=0.01))
    test_db.commit()

    response = client.get("/api/v1/logs", params={"limit": 2})

    assert response.status_code == 200
    assert len(response.json()) == 2
