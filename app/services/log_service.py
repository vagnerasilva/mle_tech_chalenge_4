from datetime import datetime, timezone

from fastapi import Request, Response
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.logs import ApiLog


def write_log(request: Request, response: Response, process_time: float) -> None:
    """Persiste um registro de auditoria da requisição.

    Mesmo padrão do mle_tech_chalenge_1 (app/services/log.py): só os campos
    de auditoria são gravados (ip, path, method, status, tempo de resposta,
    timestamp) — sem corpo de request/response.
    """
    db = next(get_db())
    try:
        log_entry = ApiLog(
            ip_address=request.client.host if request.client else None,
            path=request.url.path,
            method=request.method,
            status_code=response.status_code,
            process_time=process_time,
            created_at=datetime.now(timezone.utc),
        )
        db.add(log_entry)
        db.commit()
    finally:
        db.close()


def get_logs(db: Session, limit: int = 500) -> list[dict]:
    """Busca os últimos `limit` logs, do mais recente para o mais antigo."""
    logs = db.query(ApiLog).order_by(desc(ApiLog.created_at)).limit(limit).all()
    return [
        {
            "id": log_entry.id,
            "method": log_entry.method,
            "path": log_entry.path,
            "status_code": log_entry.status_code,
            "process_time": log_entry.process_time,
            "ip_address": log_entry.ip_address,
            "created_at": log_entry.created_at.isoformat() if log_entry.created_at else None,
        }
        for log_entry in logs
    ]
