import logging
from dataclasses import dataclass

from core.cache import CacheService
from core.cache_keys import CacheKeys
from core.exceptions import BadRequestError, CourseNotFoundError, UserNotFoundError
from models.course import Course
from models.user import User
from repositories.course import CourseRepository
from repositories.refresh_token import RefreshTokenRepository
from repositories.user import UserRepository
from schemas.admin import (
    AdminCourseSchema,
    AdminUserSchema,
    PaginatedAdminCourseListSchema,
    PaginatedAdminUserListSchema,
)
from schemas.course import CourseDetailSchema, PaginationSchema


logger = logging.getLogger(__name__)


@dataclass
class AdminService:
    user_repository: UserRepository
    course_repository: CourseRepository
    refresh_repository: RefreshTokenRepository
    cache: CacheService

    async def block_user(
        self,
        admin_id: int,
        user_id: int,
    ) -> AdminUserSchema:
        if admin_id == user_id:
            raise BadRequestError(
                "Администратор не может заблокировать самого себя"
            )

        user = await self.user_repository.find_user_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        user = await self.user_repository.set_blocked(user, True)
        await self.refresh_repository.revoke_all_for_user(user_id)

        logger.info(
            "User blocked by admin: admin_id=%s user_id=%s",
            admin_id,
            user_id,
        )
        return self._build_user(user)

    async def unblock_user(self, user_id: int) -> AdminUserSchema:
        user = await self.user_repository.find_user_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        user = await self.user_repository.set_blocked(user, False)
        logger.info("User unblocked by admin: user_id=%s", user_id)
        return self._build_user(user)

    async def get_blocked_users(
        self,
        limit: int,
        offset: int,
    ) -> PaginatedAdminUserListSchema:
        users = await self.user_repository.find_blocked_users_paginated(
            limit=limit,
            offset=offset,
        )
        total = await self.user_repository.count_blocked_users()
        return PaginatedAdminUserListSchema(
            items=[self._build_user(user) for user in users],
            meta=PaginationSchema(total=total, limit=limit, offset=offset),
        )

    async def restrict_course_public_access(
        self,
        admin_id: int,
        course_id: int,
    ) -> CourseDetailSchema:
        course = await self.course_repository.get_course_by_id(course_id)
        if course is None:
            raise CourseNotFoundError()

        course = await self.course_repository.set_admin_public_access(
            course,
            is_public=False,
            is_public_allowed=False,
        )
        logger.info(
            "Course public access restricted by admin: admin_id=%s course_id=%s",
            admin_id,
            course_id,
        )
        await self._invalidate_public_course_cache(course_id)
        return CourseDetailSchema.model_validate(
            course,
            from_attributes=True,
        )

    async def restore_course_public_access(
        self,
        course_id: int,
    ) -> CourseDetailSchema:
        course = await self.course_repository.get_course_by_id(course_id)
        if course is None:
            raise CourseNotFoundError()

        course = await self.course_repository.set_admin_public_access(
            course,
            is_public=True,
            is_public_allowed=True,
        )
        logger.info(
            "Course public access restored by admin: course_id=%s",
            course_id,
        )
        await self._invalidate_public_course_cache(course_id)
        return CourseDetailSchema.model_validate(
            course,
            from_attributes=True,
        )

    async def get_restricted_courses(
        self,
        limit: int,
        offset: int,
    ) -> PaginatedAdminCourseListSchema:
        courses = await self.course_repository.find_restricted_courses_paginated(
            limit=limit,
            offset=offset,
        )
        total = await self.course_repository.count_restricted_courses()
        return PaginatedAdminCourseListSchema(
            items=[self._build_course(course) for course in courses],
            meta=PaginationSchema(total=total, limit=limit, offset=offset),
        )

    @staticmethod
    def _build_user(user: User) -> AdminUserSchema:
        return AdminUserSchema(
            id=user.id,
            email=user.email,
            username=user.username,
            profile_description=user.profile_description,
            is_blocked=user.is_blocked,
            role=user.role.name,
        )

    @staticmethod
    def _build_course(course: Course) -> AdminCourseSchema:
        return AdminCourseSchema(
            id=course.id,
            creator_id=course.creator_id,
            creator_email=course.creator.email,
            creator_username=course.creator.username,
            title=course.title,
            comment=course.comment,
            is_public=course.is_public,
            is_public_allowed=course.is_public_allowed,
            created_at=course.created_at,
        )

    async def _invalidate_public_course_cache(self, course_id: int) -> None:
        await self.cache.delete(CacheKeys.public_course(course_id))
        await self.cache.delete_pattern(CacheKeys.public_courses_pattern())
