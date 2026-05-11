from dataclasses import dataclass

from core.cache import CacheService
from core.cache_keys import CacheKeys
from core.dto import SubtopicProgressUpdate
from core.enums import Difficulty
from models.progress import CourseProgressStatusEnum
from repositories.course_progress import CourseProgressRepository
from repositories.subtopic import SubtopicRepository
from repositories.subtopic_progress import SubtopicProgressRepository


@dataclass
class CourseCacheInvalidationService:
    cache: CacheService

    async def invalidate_course_cache(self, course_id: int) -> None:
        await self.invalidate_public_course_cache(course_id)
        await self.cache.delete_pattern(
            CacheKeys.tests_for_course_pattern(course_id)
        )
        await self.cache.delete_pattern(
            CacheKeys.test_reviews_for_course_pattern(course_id)
        )

    async def invalidate_user_course_cache(
        self,
        user_id: int,
        course_id: int,
    ) -> None:
        await self.cache.delete_pattern(
            CacheKeys.tests_for_user_course_pattern(user_id, course_id)
        )
        await self.cache.delete_pattern(
            CacheKeys.test_reviews_for_user_course_pattern(user_id, course_id)
        )

    async def invalidate_public_course_cache(self, course_id: int) -> None:
        await self.cache.delete(CacheKeys.public_course(course_id))
        await self.invalidate_public_courses_cache()

    async def invalidate_public_courses_cache(self) -> None:
        await self.cache.delete_pattern(CacheKeys.public_courses_pattern())


@dataclass
class CourseLearningStateService:
    course_progress_repository: CourseProgressRepository
    subtopic_repository: SubtopicRepository
    subtopic_progress_repository: SubtopicProgressRepository

    async def ensure_learning_state(
        self,
        user_id: int,
        course_id: int,
        initial_difficulty: Difficulty,
    ) -> None:
        course_progress = (
            await self.course_progress_repository.find_by_course_and_user(
                course_id=course_id,
                user_id=user_id,
            )
        )
        if course_progress is None:
            await self.course_progress_repository.create(
                course_id=course_id,
                user_id=user_id,
                status=CourseProgressStatusEnum.ACTIVE,
            )

        subtopics = await self.subtopic_repository.find_by_course_id(
            course_id=course_id,
        )
        subtopic_ids = [subtopic.id for subtopic in subtopics]
        existing_progress = await self.subtopic_progress_repository.find_by_user_and_subtopic_ids(
            user_id=user_id,
            subtopic_ids=subtopic_ids,
        )
        existing_ids = {item.subtopic_id for item in existing_progress}

        missing_updates = [
            SubtopicProgressUpdate(
                subtopic_id=subtopic_id,
                mastery_score=0.0,
                current_difficulty=int(initial_difficulty),
                current_streak=0,
            )
            for subtopic_id in subtopic_ids
            if subtopic_id not in existing_ids
        ]
        await self.subtopic_progress_repository.upsert_many(
            user_id=user_id,
            updates=missing_updates,
        )
