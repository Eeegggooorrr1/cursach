from dataclasses import dataclass

from core.enums import Difficulty
from models.user import RoleEnum
from schemas.course import (
    CourseDashboardSummarySchema,
    CourseDetailSchema,
    CourseEnrollmentResponseSchema,
    CourseMembershipSchema,
    CourseProgressResponseSchema,
    PaginatedCourseDetailSchema,
    PaginatedCourseListSchema,
    PublicCourseDetailSchema,
)
from services.course.course_creation import CourseCreationService
from services.course.course_access import (
    CourseDeletionService,
    CoursePublicService,
)
from services.course.course_detail import CourseDetailService
from services.course.course_list import CourseListService


@dataclass
class CourseService:
    creation_service: CourseCreationService
    list_service: CourseListService
    deletion_service: CourseDeletionService
    public_service: CoursePublicService
    detail_service: CourseDetailService

    async def create_course(
        self,
        user_id: int,
        title: str,
        comment: str | None,
        prompt: str | None,
        topics: list[str],
        initial_difficulty: Difficulty,
        is_public: bool,
    ):
        return await self.creation_service.create_course(
            user_id=user_id,
            title=title,
            comment=comment,
            prompt=prompt,
            topics=topics,
            initial_difficulty=initial_difficulty,
            is_public=is_public,
        )

    async def get_user_courses(
        self,
        user_id: int,
        limit: int,
        offset: int,
    ) -> PaginatedCourseListSchema:
        return await self.list_service.get_user_courses(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )

    async def get_dashboard_summary(
        self,
        user_id: int,
    ) -> CourseDashboardSummarySchema:
        return await self.list_service.get_dashboard_summary(user_id=user_id)

    async def get_public_courses(
        self,
        limit: int,
        offset: int,
    ) -> PaginatedCourseListSchema:
        return await self.list_service.get_public_courses(
            limit=limit,
            offset=offset,
        )

    async def delete_course_for_user(
        self,
        user_id: int,
        course_id: int,
    ) -> None:
        await self.deletion_service.delete_course_for_user(
            user_id=user_id,
            course_id=course_id,
        )

    async def get_public_course_detail(
        self,
        course_id: int,
    ) -> PublicCourseDetailSchema:
        return await self.public_service.get_public_course_detail(
            course_id=course_id,
        )

    async def enroll_public_course(
        self,
        user_id: int,
        course_id: int,
        initial_difficulty: Difficulty,
    ) -> CourseEnrollmentResponseSchema:
        return await self.public_service.enroll_public_course(
            user_id=user_id,
            course_id=course_id,
            initial_difficulty=initial_difficulty,
        )

    async def get_course_membership(
        self,
        user_id: int,
        course_id: int,
    ) -> CourseMembershipSchema:
        return await self.public_service.get_course_membership(
            user_id=user_id,
            course_id=course_id,
        )

    async def set_course_visibility(
        self,
        user_id: int,
        course_id: int,
        is_public: bool,
    ) -> CourseDetailSchema:
        return await self.public_service.set_course_visibility(
            user_id=user_id,
            course_id=course_id,
            is_public=is_public,
        )

    async def get_course_detail(
        self,
        user_id: int,
        user_role: RoleEnum,
        course_id: int,
        limit: int,
        offset: int,
    ) -> PaginatedCourseDetailSchema:
        return await self.detail_service.get_course_detail(
            user_id=user_id,
            user_role=user_role,
            course_id=course_id,
            limit=limit,
            offset=offset,
        )

    async def get_course_progress(
        self,
        user_id: int,
        course_id: int,
    ) -> CourseProgressResponseSchema:
        return await self.detail_service.get_course_progress(
            user_id=user_id,
            course_id=course_id,
        )
