#!/usr/bin/env python
"""CLI para treinar o modelo LSTM de ponta a ponta (coleta -> treino -> avaliação -> salvamento).

Uso:
    python scripts/train_model.py --symbol BBD --start 2020-06-01 --end 2026-06-01 \\
        --sequence-length 30 --epochs 100 --batch-size 16
"""

import argparse
import json
import sys

from ml.data import DataCollectionError
from ml.model import run_training_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Treina o modelo LSTM de previsão de fechamento.")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--sequence-length", type=int, default=30)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    try:
        metadata = run_training_pipeline(
            symbol=args.symbol,
            start_date=args.start,
            end_date=args.end,
            sequence_length=args.sequence_length,
            epochs=args.epochs,
            batch_size=args.batch_size,
        )
    except DataCollectionError as exc:
        print(f"Erro no treinamento: {exc}", file=sys.stderr)
        return 1

    print(f"Modelo {metadata['model_name']} treinado e salvo em {metadata['model_path']}")
    print(json.dumps(metadata["metrics"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
