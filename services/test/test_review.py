from dataclasses import dataclass

from core.cache import CacheService
from core.cache_keys import CacheKeys
from core.exceptions import TestNotFoundError, TestReviewNotAvailableError
from models.progress import TestProgressStatusEnum
from repositories.question_attempt import QuestionAttemptRepository
from repositories.test import TestRepository
from repositories.test_progress import TestProgressRepository
from schemas.course import (
    ReviewAttemptSchema,
    ReviewTestSchema,
    TestReviewResponseSchema,
)


@dataclass
class TestReviewService:
    test_repository: TestRepository
    test_progress_repository: TestProgressRepository
    question_attempt_repository: QuestionAttemptRepository
    cache: CacheService

    async def get_review(
        self,
        user_id: int,
        course_id: int,
        test_id: int,
    ) -> TestReviewResponseSchema:
        cached = await self.cache.get_schema(
            CacheKeys.test_review(user_id, course_id, test_id),
            TestReviewResponseSchema,
        )
        if cached is not None:
            return cached

        test = await self.test_repository.get_test_with_details(
            test_id=test_id
        )
        if (
            test is None
            or test.course_id != course_id
            or test.user_id != user_id
        ):
            raise TestNotFoundError()

        progress = await self.test_progress_repository.find_by_user_and_test(
            user_id=user_id,
            test_id=test_id,
        )
        if (
            progress is None
            or progress.status != TestProgressStatusEnum.FINISHED
        ):
            raise TestReviewNotAvailableError()

        attempts = (
            await self.question_attempt_repository.find_by_test_progress_id(
                test_progress_id=progress.id,
            )
        )

        response = TestReviewResponseSchema(
            test=ReviewTestSchema.from_orm_test(test),
            attempts=[
                ReviewAttemptSchema(
                    question_id=attempt.question_id,
                    selected_option_ids=self._selected_option_ids(attempt),
                    is_correct=attempt.is_correct,
                )
                for attempt in attempts
            ],
        )
        await self.cache.set_schema(
            CacheKeys.test_review(user_id, course_id, test_id),
            response,
            ttl_seconds=self.cache.settings.TEST_REVIEW_CACHE_TTL_SECONDS,
        )
        return response

    @staticmethod
    def _selected_option_ids(attempt) -> list[int]:
        return sorted(
            item.answer_option_id for item in attempt.selected_options
        )
