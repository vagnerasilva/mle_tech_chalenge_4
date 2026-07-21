from functools import lru_cache
from pathlib import Path
from typing import Any


@lru_cache
def load_model(model_path: Path) -> Any:
    import tensorflow as tf

    return tf.keras.models.load_model(model_path)


@lru_cache
def load_scaler(scaler_path: Path) -> Any:
    import joblib

    return joblib.load(scaler_path)


def artifacts_available(model_path: Path, scaler_path: Path) -> bool:
    return model_path.is_file() and scaler_path.is_file()
