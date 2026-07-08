import json
import uuid
from datetime import datetime

import pytest
from starlette.responses import StreamingResponse
from starlette.requests import Request

from app.models.logs import ApiLog
from app.services import log as log_service


def make_request(scope_overrides=None):
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/test",
        "headers": [(b"content-type", b"application/json")],
        "client": ("127.0.0.1", 12345),
        "query_string": b"",
        "root_path": "",
        "scheme": "http",
    }
    if scope_overrides:
        scope.update(scope_overrides)
    return Request(scope)


def test_api_log_model_persistence(test_db):
    """Verifica que um ApiLog é persistido corretamente."""
    log = ApiLog(
        ip_address="127.0.0.1",
        path="/api/test",
        method="GET",
        status_code=200,
        request_body={"a": 1},
        response_body={"ok": True},
        query_params={"q": "1"},
        path_params={},
        process_time=0.5,
    )

    test_db.add(log)
    test_db.commit()
    test_db.refresh(log)

    assert log.id is not None
    assert isinstance(log.created_at, datetime)
    assert log.ip_address == "127.0.0.1"
    assert log.method == "GET"
    assert log.status_code == 200


def test_write_log_creates_entry(test_db, monkeypatch):
    """Chama write_log e confirma que gravou no banco."""
    # Create a separate session for the service to avoid it closing fixture session
    from sqlalchemy.orm import sessionmaker

    SessionLocal = sessionmaker(bind=test_db.bind)
    service_db = SessionLocal()

    # monkeypatch get_db used inside app.services.log to yield our session
    monkeypatch.setattr(log_service, "get_db", lambda: iter([service_db]))

    req = make_request({
        "headers": [(b"content-type", b"application/json")],
        "client": ("10.0.0.1", 54321),
        "path": "/api/test-path",
        "method": "PUT",
    })

    res = StreamingResponse(content=b"{\"result\": true}", media_type="application/json", status_code=201)
    req_body = {"value": 42}
    res_body = json.dumps({"result": True})
    process_time = 0.123

    # Call the function under test
    log_service.write_log(req, res, req_body, res_body, process_time)

    # Query using the main test_db to confirm persistence
    logs = test_db.query(ApiLog).all()
    assert len(logs) >= 1

    last = logs[-1]
    assert last.path == "/api/test-path"
    assert last.method == "PUT"
    assert last.status_code == 201
    assert last.ip_address == "10.0.0.1"
    # write_log now persists only the selected fields; bodies are not stored
    assert last.request_body is None
    assert last.response_body is None

    # Cleanup
    service_db.close()


def test_get_api_logs_endpoint(client, test_db):
    """Testa endpoint /api_logs retorna os logs salvos."""
    # seed a log
    log = ApiLog(
        ip_address="1.2.3.4",
        path="/api/seed",
        method="GET",
        status_code=200,
        request_body=None,
        response_body={"ok": True},
        query_params=None,
        path_params=None,
        process_time=0.01,
    )
    test_db.add(log)
    test_db.commit()

    response = client.get("/api_logs")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert any(item.get("path") == "/api/seed" for item in data)
    assert any(item.get("method") == "GET" for item in data)
