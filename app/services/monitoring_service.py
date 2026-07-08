"""Monitoramento básico da API — reaproveita a tabela ApiLog já preenchida
pelo middleware de logging em app/app.py (ver app/services/log.py)."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.logs import ApiLog


def get_monitoring_metrics(db: Session) -> dict:
    total_calls = db.query(func.count(ApiLog.id)).scalar() or 0

    avg_time = db.query(func.avg(ApiLog.process_time)).scalar()
    avg_response_time_ms = round(avg_time * 1000, 2) if avg_time is not None else None

    status_rows = db.query(ApiLog.status_code, func.count(ApiLog.id)).group_by(ApiLog.status_code).all()
    status_counts = {str(status): count for status, count in status_rows}

    recent = (
        db.query(ApiLog)
        .filter(ApiLog.path.like("%/predict%"))
        .order_by(ApiLog.created_at.desc())
        .limit(10)
        .all()
    )
    recent_predictions = [
        {
            "date": r.created_at.isoformat() if r.created_at else None,
            "status_code": r.status_code,
            "process_time_ms": round(r.process_time * 1000, 2),
        }
        for r in recent
    ]

    return {
        "total_calls": total_calls,
        "avg_response_time_ms": avg_response_time_ms,
        "status_counts": status_counts,
        "recent_predictions": recent_predictions,
        "api_status": "ok",
    }
