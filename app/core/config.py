
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str
    database_url: str

    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    postgres_user: str = "postgres"
    postgres_password: str
    postgres_db: str = "fastapi_db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
