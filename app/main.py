import os
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTask

from app.api.v1 import health
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.models.base import Base, engine
from app.services.log_service import write_log

settings = get_settings()

# Mesmo padrão do mle_tech_chalenge_1 (create_db.py): garante que a tabela
# api_logs exista antes da primeira requisição.
Base.metadata.create_all(bind=engine)

# Rota que consulta os próprios logs — não deve gerar um novo log a cada consulta.
_LOGS_ROUTE_PATH = "/api/v1/logs"

app = FastAPI(
    title=settings.app_name,
    description=(
        "API de previsão de preços de fechamento de ações com um modelo "
        "LSTM Bidirecional (Keras/TensorFlow). O modelo foi treinado para o "
        "ticker **BBD** (Bradesco ADR — NYSE); veja "
        "`docs/documentacao_lstm_tech_challenge.md` para o pipeline completo "
        "de treino e `/predict/single` para o exemplo de uso mais simples."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    """Grava um registro de auditoria para toda requisição da API.

    Mesmo padrão do mle_tech_chalenge_1 (middleware em app/app.py +
    app/services/log.py): mede o tempo de resposta e agenda a persistência
    como BackgroundTask (não atrasa a resposta ao cliente). A própria rota
    de consulta (`/api/v1/logs`) é excluída para não poluir o histórico com
    as consultas ao histórico.
    """
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time

    if request.url.path != _LOGS_ROUTE_PATH:
        response.background = BackgroundTask(write_log, request, response, process_time)
    return response


app.include_router(health.router)
app.include_router(api_router, prefix="/api/v1")

# Frontend (SPA) — mantém os mesmos caminhos servidos pela versão anterior.
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", include_in_schema=False)
def serve_frontend():
    index = static_dir / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"error": "frontend não encontrado"}


@app.get("/{full_path:path}", include_in_schema=False)
def serve_spa(full_path: str):
    # Catch-all para suportar client-side routing da SPA. Registrado por
    # último para não sombrear as rotas de /health, /readiness e /api/v1/*.
    index = static_dir / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"error": "frontend não encontrado"}


if __name__ == "__main__":
    import uvicorn

    # Render.com passa a porta via variável de ambiente PORT.
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
