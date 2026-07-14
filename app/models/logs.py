from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String

from app.models.base import Base


class ApiLog(Base):
    """Mesmo padrão de auditoria do mle_tech_chalenge_1 (app/models/logs.py):
    uma linha por requisição, gravada via BackgroundTask pelo middleware de
    app/main.py. `request_body`/`response_body`/`query_params`/`path_params`
    existem no schema para compatibilidade, mas — assim como no desafio 1 —
    write_log() só popula os campos de auditoria (sem corpo)."""

    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String, nullable=True)
    path = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    request_body = Column(JSON, nullable=True)
    response_body = Column(JSON, nullable=True)
    query_params = Column(JSON, nullable=True)
    path_params = Column(JSON, nullable=True)
    process_time = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
