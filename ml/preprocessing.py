import numpy as np
import pandas as pd

PRICE_COLS = ["Close", "High", "Low", "Open"]


def apply_log1p(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica log1p nas colunas de preço e volume — mesma transformação do treino."""
    out = df.copy()
    price_cols = [c for c in PRICE_COLS if c in out.columns]
    out[price_cols] = np.log1p(out[price_cols])
    if "Volume" in out.columns:
        out["Volume"] = np.log1p(out["Volume"])
    return out


def inverse_close(values: np.ndarray, scaler, num_features: int) -> np.ndarray:
    """Desfaz StandardScaler + log1p sobre a coluna Close (índice 0)."""
    dummy = np.zeros((len(values), num_features))
    dummy[:, 0] = values
    log_prices = scaler.inverse_transform(dummy)[:, 0]
    return np.expm1(log_prices)
