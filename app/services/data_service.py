import os

from ml.data import DataCollectionError, collect_raw_data


def collect(payload) -> dict:
    df = collect_raw_data(payload.symbol, payload.start_date, payload.end_date, save=True)
    symbol = payload.symbol.strip().upper()
    file_path = os.path.join("data", "raw", f"{symbol}_{payload.start_date}_{payload.end_date}.csv")
    return {
        "symbol": symbol,
        "start_date": payload.start_date,
        "end_date": payload.end_date,
        "rows_collected": len(df),
        "file_path": file_path,
        "columns": list(df.columns),
    }


__all__ = ["DataCollectionError", "collect"]
