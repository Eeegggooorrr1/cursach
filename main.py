from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import Settings
from core.di.container import build_container
from core.exceptions import AppError
from core.logging import configure_logging
from exception_handlers import app_error_handler, exception_handler
from handlers.auth import router as auth_router
from handlers.tests import router as tests_router
from handlers.courses import router as courses_router
from handlers.profile import router as profile_router


settings = Settings()
configure_logging(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await container.close()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(tests_router)
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

container = build_container()
setup_dishka(container=container, app=app)


