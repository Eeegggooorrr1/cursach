from dataclasses import dataclass

from schemas.course import TestReviewResponseSchema
from schemas.test import TestReadSchema
from services.test.test_generation import TestGenerationService
from services.test.test_read import TestReadService
from services.test.test_review import TestReviewService


@dataclass
class TestService:
    generation_service: TestGenerationService
    read_service: TestReadService
    review_service: TestReviewService

    async def create_test(self, course_id: int, user_id: int) -> TestReadSchema:
        return await self.generation_service.create_test(
            course_id=course_id,
            user_id=user_id,
        )

    async def get_test(
        self,
        course_id: int,
        test_id: int,
        user_id: int,
    ) -> TestReadSchema:
        return await self.read_service.get_test(
            course_id=course_id,
            test_id=test_id,
            user_id=user_id,
        )

    async def get_review(
        self,
        user_id: int,
        course_id: int,
        test_id: int,
    ) -> TestReviewResponseSchema:
        return await self.review_service.get_review(
            user_id=user_id,
            course_id=course_id,
            test_id=test_id,
        )
