"""Pré-processamento de séries temporais financeiras para o modelo LSTM.

Pipeline (replica o notebook de experimentos em notebooks/experiments.ipynb):
    1. Selecionar as colunas [Close, High, Low, Open, Volume]
    2. Aplicar log1p (estabiliza variância / remove skew)
    3. Normalizar com StandardScaler (fit somente no split de treino)
    4. Criar janelas deslizantes (sequence_length) para o LSTM
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

FEATURE_COLS = ["Close", "High", "Low", "Open", "Volume"]
TARGET_COL_INDEX = 0  # Close é sempre a primeira feature / alvo do modelo


def apply_log1p(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df[FEATURE_COLS] = np.log1p(df[FEATURE_COLS])
    return df


def temporal_split(values: np.ndarray, train_split: float = 0.70, val_split: float = 0.15):
    """Divide um array em treino/val/teste respeitando a ordem temporal (sem shuffle)."""
    n = len(values)
    train_size = int(n * train_split)
    val_size = int(n * val_split)

    train = values[:train_size]
    val = values[train_size:train_size + val_size]
    test = values[train_size + val_size:]
    return train, val, test


def fit_scaler(train_raw: np.ndarray) -> StandardScaler:
    scaler = StandardScaler()
    scaler.fit(train_raw)
    return scaler


def create_sequences(data: np.ndarray, sequence_length: int):
    """Gera janelas (X) e alvos (y=Close) para o LSTM. Não embaralha (série temporal)."""
    X, y = [], []
    for i in range(len(data) - sequence_length):
        X.append(data[i: i + sequence_length, :])
        y.append(data[i + sequence_length, TARGET_COL_INDEX])
    return np.array(X), np.array(y)


def inverse_close(scaled_close: np.ndarray, scaler: StandardScaler, num_features: int) -> np.ndarray:
    """Desfaz StandardScaler + log1p para uma coluna de Close (1D) e retorna preço real."""
    scaled_close = np.asarray(scaled_close).reshape(-1)
    dummy = np.zeros((len(scaled_close), num_features))
    dummy[:, TARGET_COL_INDEX] = scaled_close
    log_prices = scaler.inverse_transform(dummy)[:, TARGET_COL_INDEX]
    return np.expm1(log_prices)


def build_feature_frame_from_points(points: list[dict], default_volume: float) -> pd.DataFrame:
    """Constrói um DataFrame com as 5 features a partir de pontos {date, close}.

    Usado na opção B do /predict, onde o usuário só fornece close price.
    High/Low/Open são aproximados como iguais ao Close e Volume usa o valor
    típico observado no treinamento (default_volume) — aproximação documentada
    no README, não um mock: o modelo real roda sobre esses dados.
    """
    df = pd.DataFrame(points)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    df["High"] = df["close"]
    df["Low"] = df["close"]
    df["Open"] = df["close"]
    df["Volume"] = default_volume
    df = df.rename(columns={"close": "Close", "date": "Date"})
    return df[["Date"] + FEATURE_COLS]
