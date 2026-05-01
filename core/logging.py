import logging
from logging.config import dictConfig


def configure_logging(level: str = "INFO") -> None:
    normalized_level = level.upper()

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
            },
            "root": {
                "handlers": ["console"],
                "level": normalized_level,
            },
            "loggers": {
                "app": {"level": normalized_level, "propagate": True},
                "ai": {"level": normalized_level, "propagate": True},
                "services": {"level": normalized_level, "propagate": True},
                "repositories": {"level": "WARNING", "propagate": True},
                "sqlalchemy.engine": {
                    "level": "WARNING",
                    "propagate": False,
                    "handlers": ["console"],
                },
                "uvicorn.access": {
                    "level": "WARNING",
                    "propagate": False,
                    "handlers": ["console"],
                },
            },
        }
    )

    logging.getLogger("app.startup").info(
        "Logging configured: level=%s",
        normalized_level,
    )
