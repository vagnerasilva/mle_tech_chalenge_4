from fastapi import APIRouter

from app.api.v1 import logs, metrics, predict, validation

api_router = APIRouter()
api_router.include_router(predict.router)
api_router.include_router(metrics.router)
api_router.include_router(logs.router)
api_router.include_router(validation.router)
