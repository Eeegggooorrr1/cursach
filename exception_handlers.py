import logging
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse

from core.exceptions import AppError

logger = logging.getLogger("app.handlers")


async def app_error_handler(request: Request, exc: AppError):
    logger.warning(
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
    return JSONResponse(status_code=getattr(exc, "status_code", 500), content=content)


async def exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception at %s: %s\n%s",
        request.url.path,
        exc,
        traceback.format_exc(),
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
