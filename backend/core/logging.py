import logging
from logging.config import dictConfig
from pathlib import Path


def configure_logging(
    level: str = "INFO",
    *,
    log_to_file: bool = False,
    log_file_path: str = "/app/logs/backend.log",
    log_file_max_bytes: int = 10485760,
    log_file_backup_count: int = 5,
) -> None:
    lvl = level.upper()
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    }
    active_handlers = ["console"]

    if log_to_file:
        path = Path(log_file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": str(path),
            "maxBytes": log_file_max_bytes,
            "backupCount": log_file_backup_count,
            "encoding": "utf-8",
        }
        active_handlers.append("file")

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                },
            },
            "handlers": handlers,
            "root": {
                "handlers": active_handlers,
                "level": lvl,
            },
            "loggers": {
                "app": {"level": lvl, "propagate": True},
                "ai": {"level": lvl, "propagate": True},
                "services": {"level": lvl, "propagate": True},
                "repositories": {"level": "WARNING", "propagate": True},
                "sqlalchemy.engine": {
                    "level": "WARNING",
                    "propagate": False,
                    "handlers": active_handlers,
                },
                "uvicorn.access": {
                    "level": "WARNING",
                    "propagate": False,
                    "handlers": active_handlers,
                },
            },
        }
    )

    logging.getLogger("app.startup").info(
        "Logging configured: level=%s log_to_file=%s log_file_path=%s",
        lvl,
        log_to_file,
        log_file_path if log_to_file else None,
    )
