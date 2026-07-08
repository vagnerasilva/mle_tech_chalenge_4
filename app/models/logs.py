from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base


class ApiLog(Base):
    __tablename__ = 'api_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key = Column(UUID(as_uuid=True), nullable=True)
    ip_address = Column(String, nullable=False)
    path = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    request_body = Column(JSON, nullable=True)
    response_body = Column(JSON, nullable=True)
    query_params = Column(JSON, nullable=True)
    path_params = Column(JSON, nullable=True)
    process_time = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
