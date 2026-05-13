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

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str | None = None

    CACHE_ENABLED: bool = True
    CACHE_DEFAULT_TTL_SECONDS: int = 600
    COURSE_CACHE_TTL_SECONDS: int = 600
    PUBLIC_COURSES_CACHE_TTL_SECONDS: int = 120
    TEST_CACHE_TTL_SECONDS: int = 86400
    TEST_REVIEW_CACHE_TTL_SECONDS: int = 86400

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REFRESH: str = "10/minute"
    RATE_LIMIT_GENERATION: str = "5/hour"

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
    def redis_url(self) -> str:
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def auth_data(self) -> dict[str, str]:
        return {
            "secret_key": self.SECRET_KEY,
            "algorithm": self.ALGORITHM,
        }


def create_settings() -> Settings:
    return Settings()
