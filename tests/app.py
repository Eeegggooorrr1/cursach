from contextlib import asynccontextmanager

from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine

from core.config import Settings
from core.di.providers.auth import AuthProvider
from core.di.providers.crypt import CryptProvider
from core.di.providers.repositories import RepositoriesProvider
from core.di.providers.services import ServicesProvider
from core.exceptions import AppError
from core.rate_limit import (
    RateLimitExceeded,
    SlowAPIMiddleware,
    limiter,
    rate_limit_exception_handler,
)
from exception_handlers import app_error_handler, exception_handler
from handlers.admin import router as admin_router
from handlers.auth import router as auth_router
from handlers.courses import router as courses_router
from handlers.profile import router as profile_router
from tests.di import (
    TestAIProvider,
    TestCacheProvider,
    TestConfigProvider,
    TestDBProvider,
)
from tests.fakes import FakeLLMClient


def create_test_app(
    *,
    settings: Settings,
    engine: AsyncEngine,
    llm_client: FakeLLMClient,
) -> FastAPI:
    container = make_async_container(
        TestConfigProvider(settings),
        TestDBProvider(engine),
        TestCacheProvider(),
        RepositoriesProvider(),
        ServicesProvider(),
        FastapiProvider(),
        CryptProvider(),
        AuthProvider(),
        TestAIProvider(llm_client),
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        await container.close()

    app = FastAPI(lifespan=lifespan)
    limiter.enabled = settings.RATE_LIMIT_ENABLED
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)
    app.add_middleware(SlowAPIMiddleware)
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(courses_router)
    app.include_router(profile_router)
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, exception_handler)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    setup_dishka(container=container, app=app)
    app.state.dishka_container = container
    return app
