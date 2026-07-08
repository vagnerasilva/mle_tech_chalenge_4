"""
conftest.py — Fixtures compartilhadas para testes unitários.
Configuração de DB mockado (só usado para a tabela de logs/monitoramento) e cliente FastAPI.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient
from app.app import app
from app.models.base import Base
from app.dependencies import get_db


# DB em memória para testes (armazena só os logs de request/monitoramento)
@pytest.fixture(scope="function")
def test_db():
    """Cria um banco de dados SQLite em memória para cada teste."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)


# Override de dependência para usar DB de teste
@pytest.fixture
def client(test_db: Session):
    """Retorna cliente FastAPI com DB mockado."""
    def override_get_db():
        return test_db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
