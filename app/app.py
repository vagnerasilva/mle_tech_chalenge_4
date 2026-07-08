import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.background import BackgroundTask
from starlette.concurrency import iterate_in_threadpool

from app.models.base import Base, engine
from app.models.logs import ApiLog  # noqa: F401 - garante o registro do modelo em Base.metadata
from app.routers import (
    data,
    health,
    home,
    log,
    ml,
    model,
    monitoring,
    nolog,
    predict,
)
from app.services.log import write_log
from app.utils.constants import API_PREFIX, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Garante que as tabelas de monitoramento existam (idempotente).
    Base.metadata.create_all(bind=engine)

    # Carrega o modelo LSTM uma única vez na inicialização (evita recarregar por request).
    from app.services import model_service
    svc = model_service.get_service()
    if svc.loaded:
        logger.info(f"Modelo carregado com sucesso: {svc.model_version} (symbol={svc.symbol})")
    else:
        logger.warning("Nenhum modelo carregado no startup — treine via POST /api/v1/model/train")

    yield


app = FastAPI(
    title="Stock LSTM Forecast API",
    description=(
        "API RESTful que serve um modelo LSTM (Long Short-Term Memory) treinado para "
        "prever o preço de fechamento de ações. Tech Challenge Fase 4 — Pós Tech MLET."
    ),
    version="1.0.0",
    servers=[
        {"url": "http://localhost:8000/", "description": "Desenvolvimento"},
    ],
    lifespan=lifespan,
)


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        req_body = await request.json()
    except Exception:
        req_body = None

    try:
        logger.info(f"Recebida requisição: {request.method} {request.url.path}")
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        res_body = [section async for section in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(res_body))

        if res_body:
            try:
                res_body = res_body[0].decode()
            except Exception:
                res_body = None
        else:
            res_body = None

        # Skip logging for the `/api_logs` endpoint to avoid recording retrievals
        if not request.url.path.startswith("/api_logs"):
            response.background = BackgroundTask(
                write_log,
                request,
                response,
                req_body,
                res_body,
                process_time,
            )
        return response
    except SQLAlchemyError as e:
        logger.error(f"Erro no banco de dados: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": "Erro no banco de dados.", "detail": f"{e}"}
        )
    except Exception as e:
        logger.error(f"Erro interno inesperado: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": "Erro interno inesperado.", "detail": f"{e}"}
        )


app.include_router(
    nolog.router,
    tags=["no_logged"]
)
app.include_router(
    log.router,
    tags=["api_logs"]
)
app.include_router(
    home.router,
    prefix=f"{API_PREFIX}/home",
    tags=["home"]
)
app.include_router(
    health.router,
    prefix=f"{API_PREFIX}/health",
    tags=["health"]
)
app.include_router(
    model.router,
    prefix=f"{API_PREFIX}/model",
    tags=["model"]
)
app.include_router(
    data.router,
    prefix=f"{API_PREFIX}/data",
    tags=["data"]
)
app.include_router(
    predict.router,
    prefix=f"{API_PREFIX}/predict",
    tags=["predict"]
)
app.include_router(
    ml.router,
    prefix=f"{API_PREFIX}/ml",
    tags=["ml"]
)
app.include_router(
    monitoring.router,
    prefix=f"{API_PREFIX}/monitoring",
    tags=["monitoring"]
)


## Importante pra poder funcionar na porta principal do Render.com
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
