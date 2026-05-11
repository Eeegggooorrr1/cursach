from dataclasses import dataclass

from core.cache import CacheService
from core.cache_keys import CacheKeys
from core.exceptions import TestNotFoundError
from repositories.test import TestRepository
from schemas.test import TestReadSchema


@dataclass
class TestReadService:
    test_repository: TestRepository
    cache: CacheService

    async def get_test(
        self,
        course_id: int,
        test_id: int,
        user_id: int,
    ) -> TestReadSchema:
        cached = await self.cache.get_schema(
            CacheKeys.test(user_id, course_id, test_id),
            TestReadSchema,
        )
        if cached is not None:
            return cached

        test = await self.test_repository.get_test_with_details(test_id=test_id)
        if (
            test is None
            or test.course_id != course_id
            or test.user_id != user_id
        ):
            raise TestNotFoundError()

        response = TestReadSchema.model_validate(
            test,
            from_attributes=True,
        )
        await self.cache.set_schema(
            CacheKeys.test(user_id, course_id, test_id),
            response,
            ttl_seconds=self.cache.settings.TEST_CACHE_TTL_SECONDS,
        )
        return response
