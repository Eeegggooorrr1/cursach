import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from core.exceptions import AppError

logger = logging.getLogger("app.handlers")


async def app_error_handler(request: Request, exc: AppError):
    status_code = getattr(exc, "status_code", 500)
    log = logger.warning if status_code >= 500 else logger.info
    log(
        "AppError: path=%s code=%s message=%s extra=%s",
        request.url.path,
        getattr(exc, "code", None),
        getattr(exc, "message", None),
        getattr(exc, "extra", None),
    )
    content = {
        "error": {
            "code": getattr(exc, "code", "internal_error"),
            "message": getattr(exc, "message", "Internal server error"),
        }
    }
    return JSONResponse(
        status_code=status_code, content=content
    )


async def exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled exception at %s: %s",
        request.url.path,
        exc,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "Internal server error",
            }
        },
    )
