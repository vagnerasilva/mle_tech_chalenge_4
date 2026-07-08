"""Serviço de inferência do modelo LSTM.

`StockForecastService` carrega modelo + scaler + metadata uma única vez
(pensado para ser instanciado no startup da API) e expõe `predict()` para
prever N dias à frente, a partir de um ticker (opção A) ou de uma série
histórica fornecida pelo cliente (opção B).

Previsão de múltiplos dias (`days_ahead > 1`) usa forecasting recursivo: o
modelo só foi treinado para prever t+1 (Close), então cada passo seguinte
reusa a própria previsão como entrada do próximo passo. Isso é uma previsão
real (passa pelo modelo a cada passo), não um mock — mas o erro acumula a
cada dia adicional, o que é documentado no README como limitação conhecida.
"""

import json
import os
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

from ml import data as data_module
from ml import preprocessing as pp

METADATA_PATH = os.path.join("models", "metadata.json")


class ModelNotLoadedError(RuntimeError):
    """Modelo/scaler/metadata não puderam ser carregados."""


class InsufficientDataError(ValueError):
    """Não há pontos suficientes para montar a sequência de entrada do modelo."""


class StockForecastService:
    def __init__(self, metadata_path: str = METADATA_PATH):
        self.metadata_path = metadata_path
        self.loaded = False
        self.metadata: dict = {}
        self.model = None
        self.scaler = None
        self._load_error: str | None = None
        self._load()

    def _load(self) -> None:
        try:
            with open(self.metadata_path) as f:
                self.metadata = json.load(f)

            self.model = tf.keras.models.load_model(self.metadata["model_path"])
            self.scaler = joblib.load(self.metadata["scaler_path"])
            self.loaded = True
        except Exception as exc:  # noqa: BLE001 - queremos capturar qualquer falha de carga
            self.loaded = False
            self._load_error = str(exc)

    def reload(self) -> None:
        """Recarrega os artefatos — chamado depois de um novo treinamento."""
        self._load()

    def _require_loaded(self) -> None:
        if not self.loaded:
            raise ModelNotLoadedError(
                f"Modelo não está carregado: {self._load_error or 'artefatos ausentes'}. "
                "Treine um modelo com POST /api/v1/model/train antes de prever."
            )

    @property
    def sequence_length(self) -> int:
        return int(self.metadata.get("sequence_length", 30))

    @property
    def num_features(self) -> int:
        return len(self.metadata.get("features", pp.FEATURE_COLS))

    @property
    def symbol(self) -> str:
        return self.metadata.get("symbol", "")

    @property
    def model_version(self) -> str:
        return self.metadata.get("model_version", "unknown")

    def _fetch_latest_window(self, symbol: str) -> pd.DataFrame:
        seq_len = self.sequence_length
        calendar_days = seq_len * 2 + 15
        end_date = datetime.today().date()
        start_date = end_date - pd.Timedelta(days=calendar_days)

        raw = data_module.collect_raw_data(
            symbol, start_date.isoformat(), end_date.isoformat(), save=False
        )
        if len(raw) < seq_len:
            raise InsufficientDataError(
                f"yfinance retornou {len(raw)} pregões para {symbol!r}, "
                f"necessário {seq_len}. Tente aumentar o intervalo ou verifique o símbolo."
            )
        return raw

    def _historical_points_to_window(self, historical_data: list[dict]) -> pd.DataFrame:
        seq_len = self.sequence_length
        if len(historical_data) < seq_len:
            raise InsufficientDataError(
                f"historical_data tem {len(historical_data)} pontos, "
                f"necessário pelo menos {seq_len} (sequence_length do modelo)."
            )
        default_volume = self.metadata.get("preprocessing", {}).get("default_volume_approx", 1.0)
        df = pp.build_feature_frame_from_points(historical_data, default_volume)
        return df.tail(seq_len).reset_index(drop=True)

    def _recursive_forecast(self, window_df: pd.DataFrame, days_ahead: int) -> list[float]:
        window_log = np.log1p(window_df[pp.FEATURE_COLS].values.astype(float))
        window_scaled = self.scaler.transform(window_log)

        volume_idx = pp.FEATURE_COLS.index("Volume")
        close_idx = pp.FEATURE_COLS.index("Close")

        predicted_prices = []
        for _ in range(days_ahead):
            X_input = window_scaled[np.newaxis, :, :]
            pred_scaled_close = float(self.model.predict(X_input, verbose=0)[0, 0])

            real_close = float(
                pp.inverse_close(np.array([pred_scaled_close]), self.scaler, self.num_features)[0]
            )
            predicted_prices.append(real_close)

            # Constrói a linha sintética do próximo dia: Close/High/Low/Open aproximados
            # pelo preço previsto, Volume mantido igual ao último pregão conhecido.
            close_log = np.log1p(real_close)
            new_row_log = np.full(self.num_features, close_log)
            new_row_log[volume_idx] = window_log[-1, volume_idx]

            new_row_scaled = self.scaler.transform(new_row_log.reshape(1, -1))[0]

            window_log = np.vstack([window_log[1:], new_row_log])
            window_scaled = np.vstack([window_scaled[1:], new_row_scaled])

        return predicted_prices

    def predict(
        self,
        symbol: str | None = None,
        historical_data: list[dict] | None = None,
        days_ahead: int = 1,
    ) -> dict:
        self._require_loaded()

        if days_ahead < 1:
            raise ValueError("days_ahead deve ser >= 1.")

        if historical_data:
            window_df = self._historical_points_to_window(historical_data)
            last_date = pd.to_datetime(window_df["Date"]).iloc[-1]
            used_symbol = symbol or "CUSTOM"
        elif symbol:
            raw = self._fetch_latest_window(symbol)
            window_df = raw.tail(self.sequence_length).reset_index(drop=True)
            last_date = pd.to_datetime(window_df["Date"]).iloc[-1]
            used_symbol = symbol.strip().upper()
        else:
            raise ValueError("Informe 'symbol' ou 'historical_data'.")

        predicted_prices = self._recursive_forecast(window_df, days_ahead)
        future_dates = pd.bdate_range(start=last_date + pd.Timedelta(days=1), periods=days_ahead)

        return {
            "symbol": used_symbol,
            "last_known_date": last_date.date().isoformat(),
            "prediction_date": future_dates[-1].date().isoformat(),
            "predicted_close": round(predicted_prices[-1], 4),
            "predictions": [
                {"date": d.date().isoformat(), "predicted_close": round(p, 4)}
                for d, p in zip(future_dates, predicted_prices)
            ],
            "days_ahead": days_ahead,
            "model_version": self.model_version,
            "sequence_length": self.sequence_length,
        }
