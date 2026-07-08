from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    model_config = SettingsConfigDict(env_file="app/.env", extra="ignore")


settings = Settings()
