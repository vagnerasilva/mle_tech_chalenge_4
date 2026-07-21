import datetime

from pydantic import BaseModel


class ApiLogEntry(BaseModel):
    id: int
    method: str
    path: str
    status_code: int
    process_time: float
    ip_address: str | None
    created_at: str | None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "method": "POST",
                    "path": "/api/v1/predict/single",
                    "status_code": 200,
                    "process_time": 0.842,
                    "ip_address": "127.0.0.1",
                    "created_at": "2026-07-13T23:48:18.640903+00:00",
                }
            ]
        }
    }
