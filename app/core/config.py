import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")

    app_name: str = "Previsão de Preços de Ações — LSTM"
    cors_origins: list[str] = ["*"]

    # Caminhos para artefatos do modelo
    # Padrão: artifacts/modelo_lstm.keras e artifacts/scaler.pkl
    model_path: Path = REPO_ROOT / "artifacts" / "modelo_lstm.keras"
    scaler_path: Path = REPO_ROOT / "artifacts" / "scaler.pkl"

    # Banco de dados centralizado (auditoria + rate limit)
    # Padrão: data/database.db
    db_path: Path = REPO_ROOT / "data" / "database.db"

    # Hiperparâmetros do modelo LSTM — CRÍTICOS
    # Precisam bater exatamente com o pipeline de treino
    # Mudar sem retreinar invalida as previsões
    look_back: int = 30
    feature_cols: list[str] = ["Close", "High", "Low", "Open", "Volume"]

    # Rate Limiting
    # Proteção contra abuso: máximo de requisições por IP em uma janela de tempo
    rate_limit_max_requests: int = 10  # Máximo 10 requisições
    rate_limit_window_seconds: int = 300  # Janela de 5 minutos (300 seg)

    @property
    def num_features(self) -> int:
        return len(self.feature_cols)


@lru_cache
def get_settings() -> Settings:
    """
    Carrega configurações de:
    1. Variáveis de ambiente (APP_* com prefixo)
    2. Arquivo .env (se existir)
    3. Valores padrão do código

    Precedência: env vars > .env > defaults
    """
    return Settings()


def is_production() -> bool:
    """Detecta se está rodando em produção (Render.com)."""
    return os.getenv("RENDER") == "true" or os.getenv("ENVIRONMENT") == "production"


def is_debug() -> bool:
    """Detecta se debug está ativado."""
    return os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
