from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from core.cache import CacheService, create_redis_client
from core.config import Settings


class CacheProvider(Provider):
    @provide(scope=Scope.APP)
    async def redis(self, settings: Settings) -> AsyncIterator[Redis]:
        redis = create_redis_client(settings)
        try:
            yield redis
        finally:
            await redis.aclose()

    @provide(scope=Scope.REQUEST)
    def cache_service(
        self,
        redis: Redis,
        settings: Settings,
    ) -> CacheService:
        return CacheService(redis=redis, settings=settings)
