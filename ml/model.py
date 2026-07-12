"""Construção, treinamento e avaliação do modelo LSTM.

Arquitetura idêntica à validada em notebooks/experiments.ipynb (busca de
hiperparâmetros via TimeSeriesSplit + grid search), reaproveitada aqui como
função determinística para permitir retreinar via script ou via API.
"""

import json
import os
from datetime import date

import joblib
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.layers import LSTM, BatchNormalization, Bidirectional, Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2

from ml import data as data_module
from ml import preprocessing as pp

SAVED_MODEL_DIR = os.path.join("models", "saved")
SCALER_DIR = os.path.join("models", "scalers")
METADATA_PATH = os.path.join("models", "metadata.json")


def build_model(sequence_length: int, num_features: int, units: int = 128, dropout: float = 0.3):
    model = Sequential([
        Bidirectional(
            LSTM(units // 2, return_sequences=True, kernel_regularizer=l2(1e-6)),
            input_shape=(sequence_length, num_features),
        ),
        BatchNormalization(),
        Dropout(dropout),
        LSTM(units // 2, return_sequences=False, kernel_regularizer=l2(1e-6)),
        BatchNormalization(),
        Dropout(dropout),
        Dense(16, activation="relu"),
        Dropout(dropout * 0.5),
        Dense(1),
    ])
    model.compile(optimizer=Adam(learning_rate=1e-4), loss="mae", metrics=["mape"])
    return model


def evaluate(model, scaler, X_test: np.ndarray, y_test: np.ndarray, num_features: int) -> dict:
    predictions = model.predict(X_test, verbose=0)

    y_pred_orig = pp.inverse_close(predictions.flatten(), scaler, num_features)
    y_test_orig = pp.inverse_close(y_test, scaler, num_features)

    mae = float(mean_absolute_error(y_test_orig, y_pred_orig))
    rmse = float(np.sqrt(mean_squared_error(y_test_orig, y_pred_orig)))
    mape = float(np.mean(np.abs((y_test_orig - y_pred_orig) / y_test_orig)) * 100)
    dir_acc = float(
        np.mean(np.sign(np.diff(y_test_orig)) == np.sign(np.diff(y_pred_orig))) * 100
    ) if len(y_test_orig) > 1 else None

    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "mape": round(mape, 2),
        "directional_accuracy": round(dir_acc, 2) if dir_acc is not None else None,
    }


def _next_model_version() -> int:
    if not os.path.exists(METADATA_PATH):
        return 1
    with open(METADATA_PATH) as f:
        meta = json.load(f)
    current = meta.get("model_version", "1.0.0")
    try:
        major = int(str(current).split(".")[0])
    except (ValueError, IndexError):
        major = 1
    return major + 1


def run_training_pipeline(
    symbol: str,
    start_date: str,
    end_date: str,
    sequence_length: int = 30,
    epochs: int = 50,
    batch_size: int = 32,
) -> dict:
    """Pipeline completa: coleta -> pré-processa -> treina -> avalia -> salva.

    Roda de forma síncrona (bloqueante) — aceitável para o escopo acadêmico
    deste projeto; treinos com muitas épocas vão demorar a resposta da API.
    """
    raw = data_module.collect_raw_data(symbol, start_date, end_date, save=True)
    df = pp.apply_log1p(raw)

    values = df[pp.FEATURE_COLS].values
    num_features = values.shape[1]

    if len(values) < sequence_length * 3:
        raise data_module.DataCollectionError(
            f"Dados insuficientes para treinar: {len(values)} pregões, "
            f"necessário pelo menos {sequence_length * 3} para um split treino/val/teste consistente."
        )

    train_raw, val_raw, test_raw = pp.temporal_split(values)

    scaler = pp.fit_scaler(train_raw)
    train_scaled = scaler.transform(train_raw)
    val_scaled = scaler.transform(val_raw)
    test_scaled = scaler.transform(test_raw)

    X_train, y_train = pp.create_sequences(train_scaled, sequence_length)
    X_val, y_val = pp.create_sequences(val_scaled, sequence_length)
    X_test, y_test = pp.create_sequences(test_scaled, sequence_length)

    if len(X_train) == 0 or len(X_val) == 0 or len(X_test) == 0:
        raise data_module.DataCollectionError(
            "Dados insuficientes após criação das janelas temporais (sequence_length muito grande "
            "para o período coletado)."
        )

    model = build_model(sequence_length, num_features)

    callbacks = [
        EarlyStopping(monitor="val_loss", patience=15, restore_best_weights=True, verbose=0),
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=5, min_lr=1e-6, verbose=0),
    ]

    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_val, y_val),
        callbacks=callbacks,
        verbose=0,
    )

    metrics = evaluate(model, scaler, X_test, y_test, num_features)
    metrics["final_loss"] = round(float(history.history["loss"][-1]), 6)
    metrics["final_val_loss"] = round(float(history.history["val_loss"][-1]), 6)

    version = _next_model_version()
    model_name = f"lstm_v{version}"
    os.makedirs(SAVED_MODEL_DIR, exist_ok=True)
    os.makedirs(SCALER_DIR, exist_ok=True)

    model_path = os.path.join(SAVED_MODEL_DIR, f"{model_name}.keras")
    scaler_path = os.path.join(SCALER_DIR, f"{model_name}_scaler.pkl")
    model.save(model_path)
    joblib.dump(scaler, scaler_path)

    default_volume = float(np.expm1(scaler.mean_[pp.FEATURE_COLS.index("Volume")]))

    metadata = {
        "model_name": model_name,
        "model_version": f"{version}.0.0",
        "model_type": "LSTM",
        "framework": "tensorflow.keras",
        "symbol": symbol.strip().upper(),
        "model_path": model_path,
        "scaler_path": scaler_path,
        "data_start_date": start_date,
        "data_end_date": end_date,
        "sequence_length": sequence_length,
        "features": pp.FEATURE_COLS,
        "target": "Close",
        "preprocessing": {
            "log1p_columns": pp.FEATURE_COLS,
            "scaler_type": "StandardScaler",
            "scaler_fit_on": "train_split_only",
            "default_volume_approx": round(default_volume, 2),
        },
        "hyperparameters": {
            "units": 128,
            "dropout": 0.3,
            "batch_size": batch_size,
            "learning_rate": 0.0001,
            "optimizer": "Adam",
            "loss": "mae",
            "epochs_max": epochs,
            "epochs_run": len(history.history["loss"]),
        },
        "dataset": {
            "total_samples": len(values),
            "train_samples": len(train_raw),
            "val_samples": len(val_raw),
            "test_samples": len(test_raw),
            "train_split": 0.70,
            "val_split": 0.15,
            "test_split": 0.15,
        },
        "metrics": metrics,
        "trained_at": date.today().isoformat(),
        "source_notebook": "notebooks/experiments.ipynb",
    }

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

    return metadata
