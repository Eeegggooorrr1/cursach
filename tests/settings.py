from pathlib import Path

from pydantic_settings import SettingsConfigDict

from core.config import Settings


class TestSettings(Settings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env.test",
        extra="ignore",
    )


def create_test_settings() -> TestSettings:
    return TestSettings()
