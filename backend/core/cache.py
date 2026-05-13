import logging
from dataclasses import dataclass
from typing import TypeVar

from pydantic import BaseModel
from redis.asyncio import Redis
from redis.exceptions import RedisError

from core.config import Settings


logger = logging.getLogger(__name__)

SchemaT = TypeVar("SchemaT", bound=BaseModel)


def create_redis_client(settings: Settings) -> Redis:
    return Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )


@dataclass
class CacheService:
    redis: Redis
    settings: Settings
    prefix: str = "course-adapt"

    async def get_schema(
        self,
        key: str,
        schema_type: type[SchemaT],
    ) -> SchemaT | None:
        if not self.settings.CACHE_ENABLED:
            return None

        try:
            payload = await self.redis.get(self._key(key))
        except RedisError:
            logger.warning("Cache read failed: key=%s", key, exc_info=True)
            return None

        if payload is None:
            return None

        try:
            return schema_type.model_validate_json(payload)
        except ValueError:
            logger.warning("Cache payload validation failed: key=%s", key)
            await self.delete(key)
            return None

    async def set_schema(
        self,
        key: str,
        value: BaseModel,
        ttl_seconds: int | None = None,
    ) -> None:
        if not self.settings.CACHE_ENABLED:
            return

        ttl = ttl_seconds or self.settings.CACHE_DEFAULT_TTL_SECONDS
        try:
            await self.redis.set(
                self._key(key),
                value.model_dump_json(),
                ex=ttl,
            )
        except RedisError:
            logger.warning("Cache write failed: key=%s", key, exc_info=True)

    async def delete(self, key: str) -> None:
        if not self.settings.CACHE_ENABLED:
            return

        try:
            await self.redis.delete(self._key(key))
        except RedisError:
            logger.warning("Cache delete failed: key=%s", key, exc_info=True)

    async def delete_pattern(self, pattern: str) -> None:
        if not self.settings.CACHE_ENABLED:
            return

        redis_pattern = self._key(pattern)
        try:
            keys = [
                key async for key in self.redis.scan_iter(match=redis_pattern)
            ]
            if keys:
                await self.redis.delete(*keys)
        except RedisError:
            logger.warning(
                "Cache pattern delete failed: pattern=%s",
                pattern,
                exc_info=True,
            )

    def _key(self, key: str) -> str:
        return f"{self.prefix}:{key}"
