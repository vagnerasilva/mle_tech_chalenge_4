#!/usr/bin/env python
"""CLI para reavaliar o modelo atualmente salvo (models/metadata.json) no split de teste.

Útil para validar as métricas sem precisar retreinar. Usa o mesmo símbolo e
intervalo de datas registrados no metadata.json.

Uso:
    python scripts/evaluate_model.py
"""

import json
import sys

from ml import preprocessing as pp
from ml.data import DataCollectionError, collect_raw_data
from ml.inference import StockForecastService
from ml.model import evaluate

METADATA_PATH = "models/metadata.json"


def main() -> int:
    svc = StockForecastService(metadata_path=METADATA_PATH)
    if not svc.loaded:
        print("Modelo não carregado — treine antes com scripts/train_model.py", file=sys.stderr)
        return 1

    meta = svc.metadata
    try:
        raw = collect_raw_data(meta["symbol"], meta["data_start_date"], meta["data_end_date"], save=False)
    except DataCollectionError as exc:
        print(f"Erro ao recarregar dados para avaliação: {exc}", file=sys.stderr)
        return 1

    df = pp.apply_log1p(raw)
    values = df[pp.FEATURE_COLS].values
    _, _, test_raw = pp.temporal_split(values)

    test_scaled = svc.scaler.transform(test_raw)
    X_test, y_test = pp.create_sequences(test_scaled, svc.sequence_length)

    metrics = evaluate(svc.model, svc.scaler, X_test, y_test, svc.num_features)
    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
