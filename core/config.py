from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    SECRET_KEY: str
    ALGORITHM: str

    REFRESH_EXPIRES_DAYS: int = 30
    ACCESS_EXPIRES_MINUTES: int = 10

    CRON_FREQ_MINUTES: int = 1

    SEED_DIR: str

    DEEPSEEK_API_KEY: str
    DEEPSEEK_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_MAX_TOKENS: int = 4096

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env"
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def auth_data(self) -> dict[str, str]:
        return {
            "secret_key": self.SECRET_KEY,
            "algorithm": self.ALGORITHM,
        }


def create_settings() -> Settings:
    return Settings()
