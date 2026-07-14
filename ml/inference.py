import datetime

import numpy as np
import pandas as pd

from app.core.config import Settings
from ml import model as model_loader
from ml.data import fetch_ohlcv
from ml.preprocessing import apply_log1p, inverse_close


def predict_next_close(symbol: str, settings: Settings) -> tuple[float, datetime.date]:
    """Prevê o preço de fechamento do próximo pregão para `symbol`."""
    model = model_loader.load_model(settings.model_path)
    scaler = model_loader.load_scaler(settings.scaler_path)

    raw = fetch_ohlcv(symbol, settings.look_back, settings.feature_cols)
    window = apply_log1p(raw[settings.feature_cols])
    window_scaled = scaler.transform(window.values)
    x_input = window_scaled[np.newaxis, :, :]

    pred_scaled = model.predict(x_input, verbose=0)
    price = float(inverse_close(pred_scaled.flatten(), scaler, settings.num_features)[0])
    last_date = raw["Date"].iloc[-1]
    return price, last_date.date() if hasattr(last_date, "date") else last_date


