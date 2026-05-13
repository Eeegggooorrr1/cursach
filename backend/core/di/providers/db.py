from collections.abc import AsyncIterator

from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
)

from core.config import Settings
from core.db import (
    create_database_engine,
    create_database_sessionmaker,
    database_session_scope,
)


class DBProvider(Provider):
    @provide(scope=Scope.APP)
    async def engine(self, settings: Settings) -> AsyncIterator[AsyncEngine]:
        engine = create_database_engine(settings)
        try:
            yield engine
        finally:
            await engine.dispose()

    @provide(scope=Scope.APP)
    def sessionmaker(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return create_database_sessionmaker(engine)

    @provide(scope=Scope.REQUEST)
    async def session(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[AsyncSession]:
        async with database_session_scope(sessionmaker) as session:
            yield session
