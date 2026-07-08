import json
import uuid
from datetime import datetime, timezone

from fastapi import Request
from starlette.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.dependencies import get_db
from app.models.logs import ApiLog


def write_log(
    req: Request, 
    res: StreamingResponse, 
    req_body: dict, 
    res_body: str, 
    process_time: float
):
    """Persist only the selected fields to match the streamlit README.

    Stored fields: ip_address, path, method, status_code, process_time, created_at
    """
    db = next(get_db())
    try:
        log = ApiLog(
            ip_address=req.client.host if req.client else None,
            path=req.url.path,
            method=req.method,
            status_code=res.status_code,
            process_time=process_time,
            created_at=datetime.now(timezone.utc),
        )
        db.add(log)
        db.commit()
    finally:
        db.close()


def get_logs(db: Session) -> list:
    #logs = db.query(ApiLog).all()
    """Busca os últimos 500 logs ordenados do mais recente para o mais antigo"""
    logs = (
        db.query(ApiLog)
        .order_by(desc(ApiLog.created_at))
        .limit(500)
        .all() 
    )


    result = []
    for l in logs:
        result.append({
            "id": l.id,
            "method": l.method,
            "path": l.path,
            "status_code": l.status_code,
            "process_time": l.process_time,
            "ip_address": l.ip_address,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        })
    return result
