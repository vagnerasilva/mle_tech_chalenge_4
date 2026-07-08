"""Endpoint de introspecção das features usadas pelo modelo (GET /api/v1/ml/features).

Substitui o antigo serviço de features de livros (removido na migração para
o domínio de previsão de ações)."""

from ml import preprocessing as pp
from ml.data import load_raw_data
from app.services.model_service import ModelNotLoadedError, get_service


def get_features() -> dict:
    svc = get_service()
    if not svc.loaded:
        raise ModelNotLoadedError("Nenhum modelo treinado/carregado ainda.")

    meta = svc.metadata
    raw = load_raw_data(meta["symbol"], meta["data_start_date"], meta["data_end_date"])
    processed = pp.apply_log1p(raw)

    raw_view = raw[["Date"] + pp.FEATURE_COLS].tail(5).copy()
    raw_view["Date"] = raw_view["Date"].astype(str)
    processed_view = processed[["Date"] + pp.FEATURE_COLS].tail(5).copy()
    processed_view["Date"] = processed_view["Date"].astype(str)

    sample_raw = raw_view.to_dict(orient="records")
    sample_processed = processed_view.to_dict(orient="records")

    return {
        "features": meta["features"],
        "target": meta.get("target", "Close"),
        "sequence_length": meta["sequence_length"],
        "preprocessing": meta.get("preprocessing", {}),
        "sample_raw": sample_raw,
        "sample_processed": sample_processed,
    }
