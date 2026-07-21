import datetime

import numpy as np
import pandas as pd
import yfinance as yf

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

    raw_last_date = raw["Date"].iloc[-1]
    last_available_date = raw_last_date.date() if hasattr(raw_last_date, "date") else raw_last_date
    execution_date = datetime.date.today()
    prediction_date = _get_next_trading_day(symbol, max(last_available_date, execution_date))

    return price, prediction_date


def _get_next_trading_day(symbol: str, base_date: datetime.date | datetime.datetime) -> datetime.date:
    if hasattr(base_date, "date"):
        base_date = base_date.date()

    try:
        start = base_date + datetime.timedelta(days=1)
        end = base_date + datetime.timedelta(days=14)
        data = yf.download(symbol, start=start, end=end, progress=False)

        if data.empty:
            return start

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        if isinstance(data.index, pd.DatetimeIndex):
            trading_dates = [idx.date() for idx in data.index if idx.date() > base_date]
            if trading_dates:
                return min(trading_dates)

        return start
    except Exception:
        return start


