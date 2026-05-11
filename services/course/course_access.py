import logging
from dataclasses import dataclass

from core.cache import CacheService
from core.cache_keys import CacheKeys
from core.enums import Difficulty
from core.exceptions import (
    CourseNotFoundError,
    CoursePublicAccessRestrictedError,
    ForbiddenError,
)
from repositories.course import CourseRepository
from schemas.course import (
    CourseDetailSchema,
    CourseEnrollmentResponseSchema,
    CourseMembershipSchema,
    PublicCourseDetailSchema,
)
from services.course.course_support import (
    CourseCacheInvalidationService,
    CourseLearningStateService,
)


logger = logging.getLogger(__name__)


@dataclass
class CourseDeletionService:
    course_repository: CourseRepository
    cache_invalidation_service: CourseCacheInvalidationService

    async def delete_course_for_user(
        self,
        user_id: int,
        course_id: int,
    ) -> None:
        course = await self.course_repository.get_course_by_id(
            course_id=course_id,
        )
        if course is None:
            raise CourseNotFoundError()

        link = await self.course_repository.find_user_course_link(
            user_id=user_id,
            course_id=course_id,
        )
        if link is None and course.creator_id != user_id:
            raise CourseNotFoundError()

        if course.creator_id != user_id and link is None:
            raise ForbiddenError()

        enrollments_count = (
            await self.course_repository.count_course_enrollments(
                course_id=course_id,
            )
        )
        if course.creator_id == user_id and enrollments_count <= 1:
            await self.course_repository.delete_course(course)
            await self.cache_invalidation_service.invalidate_course_cache(
                course_id=course_id,
            )
            logger.info(
                "Course deleted: user_id=%s course_id=%s mode=full",
                user_id,
                course_id,
            )
            return

        await self.course_repository.delete_user_course_data(
            user_id=user_id,
            course_id=course_id,
        )
        await self.cache_invalidation_service.invalidate_user_course_cache(
            user_id=user_id,
            course_id=course_id,
        )
        logger.info(
            "Course user data deleted: user_id=%s course_id=%s mode=user_only",
            user_id,
            course_id,
        )


@dataclass
class CoursePublicService:
    course_repository: CourseRepository
    learning_state_service: CourseLearningStateService
    cache_invalidation_service: CourseCacheInvalidationService
    cache: CacheService

    async def get_public_course_detail(
        self,
        course_id: int,
    ) -> PublicCourseDetailSchema:
        cache_key = CacheKeys.public_course(course_id)
        cached = await self.cache.get_schema(cache_key, PublicCourseDetailSchema)
        if cached is not None:
            return cached

        course = await self.course_repository.find_public_with_details(
            course_id=course_id,
        )
        if course is None:
            raise CourseNotFoundError()

        response = PublicCourseDetailSchema.model_validate(
            course,
            from_attributes=True,
        )
        await self.cache.set_schema(
            cache_key,
            response,
            ttl_seconds=self.cache.settings.COURSE_CACHE_TTL_SECONDS,
        )
        return response

    async def enroll_public_course(
        self,
        user_id: int,
        course_id: int,
        initial_difficulty: Difficulty,
    ) -> CourseEnrollmentResponseSchema:
        course = await self.course_repository.get_course_by_id(
            course_id=course_id
        )
        if course is None or not course.is_public:
            raise CourseNotFoundError()

        enrolled = await self.course_repository.add_user_course(
            user_id=user_id,
            course_id=course_id,
        )

        await self.learning_state_service.ensure_learning_state(
            user_id=user_id,
            course_id=course_id,
            initial_difficulty=initial_difficulty,
        )

        logger.info(
            "Public course enrollment: user_id=%s course_id=%s enrolled=%s initial_difficulty=%s",
            user_id,
            course_id,
            enrolled,
            int(initial_difficulty),
        )

        return CourseEnrollmentResponseSchema(
            course_id=course_id,
            user_id=user_id,
            enrolled=enrolled,
        )

    async def get_course_membership(
        self,
        user_id: int,
        course_id: int,
    ) -> CourseMembershipSchema:
        course = await self.course_repository.get_course_by_id(
            course_id=course_id,
        )
        if course is None:
            raise CourseNotFoundError()

        link = await self.course_repository.find_user_course_link(
            user_id=user_id,
            course_id=course_id,
        )
        return CourseMembershipSchema(
            course_id=course_id,
            user_id=user_id,
            enrolled=link is not None,
            owned=course.creator_id == user_id,
        )

    async def set_course_visibility(
        self,
        user_id: int,
        course_id: int,
        is_public: bool,
    ) -> CourseDetailSchema:
        course = await self.course_repository.find_owned_by_id(
            course_id=course_id,
            creator_id=user_id,
        )
        if course is None:
            raise CourseNotFoundError()

        if is_public and not course.is_public_allowed:
            raise CoursePublicAccessRestrictedError()

        course = await self.course_repository.set_visibility(
            course=course,
            is_public=is_public,
        )
        logger.info(
            "Course visibility changed: user_id=%s course_id=%s is_public=%s",
            user_id,
            course_id,
            is_public,
        )
        await self.cache_invalidation_service.invalidate_public_course_cache(
            course_id=course_id,
        )
        return CourseDetailSchema.model_validate(
            course,
            from_attributes=True,
        )
