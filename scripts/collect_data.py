#!/usr/bin/env python
"""CLI para coletar dados históricos de uma ação via yfinance.

Uso:
    python scripts/collect_data.py --symbol BBD --start 2020-06-01 --end 2026-06-01
"""

import argparse
import sys

from ml.data import DataCollectionError, collect_raw_data


def main() -> int:
    parser = argparse.ArgumentParser(description="Coleta dados históricos OHLCV via yfinance.")
    parser.add_argument("--symbol", required=True, help="Ticker, ex.: BBD, AAPL, PETR4.SA")
    parser.add_argument("--start", required=True, help="Data inicial (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="Data final (YYYY-MM-DD)")
    args = parser.parse_args()

    try:
        df = collect_raw_data(args.symbol, args.start, args.end, save=True)
    except DataCollectionError as exc:
        print(f"Erro na coleta: {exc}", file=sys.stderr)
        return 1

    print(f"Coletados {len(df)} pregões para {args.symbol.upper()} ({args.start} -> {args.end})")
    print(f"Salvo em data/raw/{args.symbol.upper()}_{args.start}_{args.end}.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
