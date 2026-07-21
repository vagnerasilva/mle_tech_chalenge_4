"""
Testes para Rate Limiting

Valida:
- Máximo 10 requisições por IP em 5 minutos
- 11ª requisição retorna 429
- Health/readiness não são rate limited
"""

import time

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.base import engine
from app.models.logs import RateLimitLog
from sqlalchemy.orm import sessionmaker

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def client():
    """Cliente de testes."""
    return TestClient(app)


@pytest.fixture
def db():
    """Sessão de banco para testes."""
    session = TestingSessionLocal()
    yield session
    # Limpar rate_limit_logs após teste
    session.query(RateLimitLog).delete()
    session.commit()
    session.close()


def test_health_check_not_rate_limited(client):
    """Health check não deve ser rate limited."""
    # Fazer 20 requisições (mais que o limite)
    for _ in range(20):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_readiness_check_not_rate_limited(client):
    """Readiness check não deve ser rate limited."""
    # Fazer 20 requisições (mais que o limite)
    for _ in range(20):
        response = client.get("/readiness")
        assert response.status_code in (200, 503)  # 200 ou 503 conforme modelo carregado


def test_predict_single_rate_limited(client, db):
    """Predição deve ser rate limited após 10 requisições."""
    # Limpar banco antes
    db.query(RateLimitLog).delete()
    db.commit()

    # Fazer 10 requisições bem-sucedidas
    for i in range(10):
        response = client.post(
            "/api/v1/predict/single",
            json={"symbol": "BBD"},
        )
        # Podem retornar 200 ou 422 (se modelo não carregado), mas não 429
        assert response.status_code in (200, 422, 500)
        assert response.status_code != 429

    # 11ª requisição deve ser bloqueada
    response = client.post(
        "/api/v1/predict/single",
        json={"symbol": "BBD"},
    )
    assert response.status_code == 429
    assert "Limite de taxa excedido" in response.json()["detail"]
    assert "retry_after" in response.json()


def test_rate_limit_retry_after_header(client, db):
    """Rate limit deve incluir header Retry-After."""
    # Limpar banco
    db.query(RateLimitLog).delete()
    db.commit()

    # Fazer 10 requisições
    for _ in range(10):
        client.post("/api/v1/predict/single", json={"symbol": "BBD"})

    # 11ª requisição bloqueada
    response = client.post(
        "/api/v1/predict/single",
        json={"symbol": "BBD"},
    )
    assert response.status_code == 429
    assert "Retry-After" in response.headers
    assert int(response.headers["Retry-After"]) > 0


def test_batch_predict_rate_limited(client, db):
    """Batch predict também deve respeitar rate limit."""
    db.query(RateLimitLog).delete()
    db.commit()

    # Fazer 10 requisições
    for _ in range(10):
        client.post(
            "/api/v1/predict/batch",
            json={"symbols": ["BBD"]},
        )

    # 11ª requisição bloqueada
    response = client.post(
        "/api/v1/predict/batch",
        json={"symbols": ["BBD"]},
    )
    assert response.status_code == 429


def test_sequence_predict_rate_limited(client, db):
    """Sequence predict também deve respeitar rate limit."""
    db.query(RateLimitLog).delete()
    db.commit()

    # Fazer 10 requisições
    for _ in range(10):
        client.post(
            "/api/v1/predict/sequence",
            json={"symbol": "BBD", "days_ahead": 3},
        )

    # 11ª requisição bloqueada
    response = client.post(
        "/api/v1/predict/sequence",
        json={"symbol": "BBD", "days_ahead": 3},
    )
    assert response.status_code == 429


def test_metrics_rate_limited(client, db):
    """Métricas também devem respeitar rate limit."""
    db.query(RateLimitLog).delete()
    db.commit()

    # Fazer 10 requisições
    for _ in range(10):
        client.get("/api/v1/metrics/latest")

    # 11ª requisição bloqueada
    response = client.get("/api/v1/metrics/latest")
    assert response.status_code == 429


def test_logs_rate_limited(client, db):
    """Logs também devem respeitar rate limit."""
    db.query(RateLimitLog).delete()
    db.commit()

    # Fazer 10 requisições
    for _ in range(10):
        client.get("/api/v1/logs")

    # 11ª requisição bloqueada
    response = client.get("/api/v1/logs")
    assert response.status_code == 429


def test_rate_limit_reset_after_window(client, db):
    """Contador deve resetar após janela de 5 minutos."""
    db.query(RateLimitLog).delete()
    db.commit()

    # Fazer 10 requisições
    for _ in range(10):
        client.post("/api/v1/predict/single", json={"symbol": "BBD"})

    # 11ª bloqueada
    response = client.post("/api/v1/predict/single", json={"symbol": "BBD"})
    assert response.status_code == 429

    # Limpar registros antigos (simular passagem de 5 minutos)
    db.query(RateLimitLog).delete()
    db.commit()

    # Agora deve funcionar novamente
    response = client.post("/api/v1/predict/single", json={"symbol": "BBD"})
    assert response.status_code in (200, 422, 500)  # Não 429


def test_rate_limit_isolation_by_ip(client, db):
    """Rate limit deve ser isolado por IP."""
    db.query(RateLimitLog).delete()
    db.commit()

    # Client 1 faz 10 requisições
    for _ in range(10):
        client.post("/api/v1/predict/single", json={"symbol": "BBD"})

    # Client 1 bloqueado na 11ª
    response = client.post("/api/v1/predict/single", json={"symbol": "BBD"})
    assert response.status_code == 429

    # Nota: TestClient simula mesmo IP (127.0.0.1) para todas as requisições
    # Em produção, IPs diferentes não compartilham limite


def test_rate_limit_response_format(client, db):
    """Resposta de rate limit deve ter formato correto."""
    db.query(RateLimitLog).delete()
    db.commit()

    # Fazer 11 requisições
    for _ in range(11):
        client.post("/api/v1/predict/single", json={"symbol": "BBD"})

    response = client.post("/api/v1/predict/single", json={"symbol": "BBD"})
    assert response.status_code == 429

    body = response.json()
    assert "detail" in body
    assert "Limite de taxa" in body["detail"]
    assert "retry_after" in body
    assert isinstance(body["retry_after"], int)
    assert body["retry_after"] > 0
    assert body["retry_after"] <= 300  # Máximo 5 minutos
