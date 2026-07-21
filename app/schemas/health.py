from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


class ReadinessResponse(BaseModel):
    ready: bool
    detail: str | None = None
