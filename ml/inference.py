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


def predict_sequence(symbol: str, days_ahead: int, settings: Settings) -> list[float]:
    """Previsão recursiva de `days_ahead` pregões à frente.

    O modelo só foi treinado para prever 1 passo à frente (Close do dia
    seguinte). Para horizontes maiores, cada previsão é realimentada como
    entrada do passo seguinte: assume-se High = Low = Open = Close previsto,
    e o Volume é mantido igual ao último valor observado. Isso é uma
    simplificação necessária (o modelo não prevê essas outras variáveis) e a
    qualidade da previsão degrada com o horizonte — trate como tendência
    aproximada, não como previsão precisa dia a dia.
    """
    model = model_loader.load_model(settings.model_path)
    scaler = model_loader.load_scaler(settings.scaler_path)

    raw = fetch_ohlcv(symbol, settings.look_back, settings.feature_cols)
    history = raw[settings.feature_cols].copy()
    last_volume = history["Volume"].iloc[-1]

    preds: list[float] = []
    for _ in range(days_ahead):
        window = apply_log1p(history.iloc[-settings.look_back :])
        window_scaled = scaler.transform(window.values)
        x_input = window_scaled[np.newaxis, :, :]

        pred_scaled = model.predict(x_input, verbose=0)
        pred_close = float(inverse_close(pred_scaled.flatten(), scaler, settings.num_features)[0])
        preds.append(pred_close)

        next_row = {"Close": pred_close, "High": pred_close, "Low": pred_close, "Open": pred_close, "Volume": last_volume}
        history = pd.concat(
            [history, pd.DataFrame([{col: next_row[col] for col in settings.feature_cols}])],
            ignore_index=True,
        )

    return preds
