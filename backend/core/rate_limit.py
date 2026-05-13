from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from core.config import create_settings


settings = create_settings()

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
    enabled=settings.RATE_LIMIT_ENABLED,
)

rate_limit_exception_handler = _rate_limit_exceeded_handler
