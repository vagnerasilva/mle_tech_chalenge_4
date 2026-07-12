"""Coleta e validação de dados históricos de ações via yfinance."""

import os
from datetime import date, datetime

import pandas as pd
import yfinance as yf

REQUIRED_COLUMNS = ["Close", "High", "Low", "Open", "Volume"]
RAW_DATA_DIR = os.path.join("data", "raw")


class DataCollectionError(ValueError):
    """Erro de negócio na coleta de dados (ticker/datas inválidas, sem dados)."""


def _validate_dates(start_date: str, end_date: str) -> None:
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        raise DataCollectionError(f"start_date inválida: {start_date!r}. Use o formato YYYY-MM-DD.")

    try:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise DataCollectionError(f"end_date inválida: {end_date!r}. Use o formato YYYY-MM-DD.")

    if start >= end:
        raise DataCollectionError("start_date deve ser anterior a end_date.")

    if end > date.today():
        raise DataCollectionError("end_date não pode estar no futuro.")


def collect_raw_data(symbol: str, start_date: str, end_date: str, save: bool = True) -> pd.DataFrame:
    """Baixa OHLCV de `symbol` via yfinance e opcionalmente salva em data/raw/.

    Levanta DataCollectionError para ticker inválido, datas inválidas ou
    ausência de dados retornados pela yfinance.
    """
    if not symbol or not symbol.strip():
        raise DataCollectionError("symbol não pode ser vazio.")

    _validate_dates(start_date, end_date)

    symbol = symbol.strip().upper()

    try:
        raw = yf.download(symbol, start=start_date, end=end_date, progress=False)
    except Exception as exc:
        raise DataCollectionError(f"Falha ao baixar dados de {symbol!r} via yfinance: {exc}") from exc

    if raw is None or raw.empty:
        raise DataCollectionError(
            f"Nenhum dado encontrado para o ticker {symbol!r} entre {start_date} e {end_date}. "
            "Verifique se o símbolo existe (ex.: 'BBD', 'AAPL', 'PETR4.SA')."
        )

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    raw.reset_index(inplace=True)

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in raw.columns]
    if missing_cols:
        raise DataCollectionError(f"Colunas ausentes no retorno da yfinance: {missing_cols}")

    raw.dropna(subset=REQUIRED_COLUMNS, inplace=True)
    raw.reset_index(drop=True, inplace=True)

    if raw.empty:
        raise DataCollectionError(f"Dados de {symbol!r} ficaram vazios após remoção de nulos.")

    if save:
        os.makedirs(RAW_DATA_DIR, exist_ok=True)
        file_path = os.path.join(RAW_DATA_DIR, f"{symbol}_{start_date}_{end_date}.csv")
        raw.to_csv(file_path, index=False)

    return raw


def load_raw_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Carrega um CSV já coletado em data/raw/, ou coleta na hora se não existir."""
    symbol = symbol.strip().upper()
    file_path = os.path.join(RAW_DATA_DIR, f"{symbol}_{start_date}_{end_date}.csv")
    if os.path.exists(file_path):
        return pd.read_csv(file_path, parse_dates=["Date"])
    return collect_raw_data(symbol, start_date, end_date, save=True)
