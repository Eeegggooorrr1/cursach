from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from jinja2 import Environment
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from ai.contracts import LLMClient
from ai.factories.course_generation_factory import CourseGenerationPromptFactory
from ai.factories.test_generation_factory import TestGenerationPromptFactory
from core.ai import create_prompt_environment
from core.cache import CacheService, create_redis_client
from core.config import Settings
from core.db import create_database_sessionmaker, database_session_scope
from tests.fakes import FakeLLMClient


class TestConfigProvider(Provider):
    def __init__(self, settings: Settings):
        super().__init__()
        self._settings = settings

    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return self._settings


class TestDBProvider(Provider):
    def __init__(self, engine: AsyncEngine):
        super().__init__()
        self._engine = engine

    @provide(scope=Scope.APP)
    def engine(self) -> AsyncEngine:
        return self._engine

    @provide(scope=Scope.APP)
    def sessionmaker(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return create_database_sessionmaker(engine)

    @provide(scope=Scope.REQUEST)
    async def session(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[AsyncSession]:
        async with database_session_scope(sessionmaker) as session:
            yield session


class TestAIProvider(Provider):
    def __init__(self, llm_client: FakeLLMClient):
        super().__init__()
        self._llm_client = llm_client

    @provide(scope=Scope.APP)
    def jinja_env(self) -> Environment:
        return create_prompt_environment()

    @provide(scope=Scope.REQUEST)
    def test_prompt_factory(
        self,
        env: Environment,
    ) -> TestGenerationPromptFactory:
        return TestGenerationPromptFactory(env=env)

    @provide(scope=Scope.REQUEST)
    def course_prompt_factory(
        self,
        env: Environment,
    ) -> CourseGenerationPromptFactory:
        return CourseGenerationPromptFactory(env=env)

    @provide(scope=Scope.APP)
    def llm_client(self) -> LLMClient:
        return self._llm_client


class TestCacheProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def cache_service(self, settings: Settings) -> CacheService:
        settings.CACHE_ENABLED = False
        return CacheService(redis=create_redis_client(settings), settings=settings)
