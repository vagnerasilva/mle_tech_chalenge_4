import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import hashlib
import random

app = FastAPI()

# Monta a pasta static (frontend) se existir
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/web")
def serve_frontend():
    index = static_dir / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"error": "frontend não encontrado"}


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


class PredictRequest(BaseModel):
    symbol: str
    days_back: int = 60
    days_ahead: int = 5


@app.post("/api/v1/predict/single")
def predict_single(payload: PredictRequest):
    """Mock de predição: retorna valores simulados reproducíveis por símbolo."""
    symbol = payload.symbol
    days_ahead = max(1, int(payload.days_ahead))

    # Gerar seed a partir do símbolo para resultados determinísticos
    h = hashlib.sha256(symbol.encode()).hexdigest()
    seed = int(h[:16], 16) % (2 ** 32)
    rnd = random.Random(seed)

    # Mock: comece em um preço base plausível (ex.: 25-300)
    base = 50 + (seed % 250)
    preds = []
    drift = 0
    for i in range(days_ahead):
        # pequena variação aleatória e tendência leve
        step = rnd.uniform(-0.02, 0.03) * base
        drift += rnd.uniform(-0.5, 0.5)
        val = round(base + step + drift, 2)
        preds.append(val)

    response = {
        "symbol": symbol,
        "predictions": preds,
        "confidence": round(0.7 + rnd.random() * 0.3, 2),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    return response


def _gen_preds_for_symbol(symbol: str, days_ahead: int):
    h = hashlib.sha256(symbol.encode()).hexdigest()
    seed = int(h[:16], 16) % (2 ** 32)
    rnd = random.Random(seed)
    base = 50 + (seed % 250)
    preds = []
    drift = 0
    for i in range(days_ahead):
        step = rnd.uniform(-0.02, 0.03) * base
        drift += rnd.uniform(-0.5, 0.5)
        val = round(base + step + drift, 2)
        preds.append(val)
    conf = round(0.7 + rnd.random() * 0.3, 2)
    return preds, conf


@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": False, "note": "mock health — modelo não carregado em mock"}


@app.get("/readiness")
def readiness_check():
    return {"ready": True, "note": "mock readiness"}


class BatchPredictRequest(BaseModel):
    symbols: list
    days_back: int = 60
    days_ahead: int = 5


@app.post("/api/v1/predict/batch")
def predict_batch(payload: BatchPredictRequest):
    out = {}
    for sym in payload.symbols:
        preds, conf = _gen_preds_for_symbol(sym, max(1, int(payload.days_ahead)))
        out[sym] = {"predictions": preds, "confidence": conf}
    return {"results": out, "timestamp": datetime.utcnow().isoformat() + "Z"}


class SequencePredictRequest(BaseModel):
    symbol: str
    days_back: int = 60
    days_ahead: int = 30


@app.post("/api/v1/predict/sequence")
def predict_sequence(payload: SequencePredictRequest):
    preds, conf = _gen_preds_for_symbol(payload.symbol, max(1, int(payload.days_ahead)))
    return {"symbol": payload.symbol, "predictions": preds, "confidence": conf, "timestamp": datetime.utcnow().isoformat() + "Z"}


@app.get("/api/v1/metrics/latest")
def metrics_latest():
    # Mock metrics
    return {
        "mae": 1.2345,
        "rmse": 2.3456,
        "mape": 3.21,
        "directional_accuracy": 62.5,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


if __name__ == "__main__":
    import uvicorn

    # Render.com passa a porta via variável de ambiente PORT
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
