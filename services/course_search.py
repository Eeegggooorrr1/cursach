from dataclasses import dataclass

from core.cache import CacheService
from core.cache_keys import CacheKeys
from repositories.course import CourseRepository
from schemas.course import (
    CourseListItemSchema,
    CoursePublicSearchSchema,
    PaginatedCourseListSchema,
    PaginationSchema,
)


@dataclass
class CourseSearchService:
    course_repository: CourseRepository
    cache: CacheService

    async def search_public_courses(
        self,
        *,
        limit: int,
        offset: int,
        filters: CoursePublicSearchSchema,
    ) -> PaginatedCourseListSchema:
        cache_key = CacheKeys.public_courses_page(
            limit=limit,
            offset=offset,
            query=filters.q,
            sort=filters.sort,
        )
        cached = await self.cache.get_schema(
            cache_key,
            PaginatedCourseListSchema,
        )
        if cached is not None:
            return cached

        courses = await self.course_repository.find_public_courses_paginated(
            limit=limit,
            offset=offset,
            query=filters.q,
            sort=filters.sort,
        )
        total = await self.course_repository.count_public_courses(
            query=filters.q,
        )

        response = PaginatedCourseListSchema(
            items=[
                CourseListItemSchema.model_validate(
                    course,
                    from_attributes=True,
                )
                for course in courses
            ],
            meta=PaginationSchema(total=total, limit=limit, offset=offset),
        )
        await self.cache.set_schema(
            cache_key,
            response,
            ttl_seconds=self.cache.settings.PUBLIC_COURSES_CACHE_TTL_SECONDS,
        )
        return response
