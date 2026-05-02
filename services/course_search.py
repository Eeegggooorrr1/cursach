from dataclasses import dataclass

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

    async def search_public_courses(
        self,
        *,
        limit: int,
        offset: int,
        filters: CoursePublicSearchSchema,
    ) -> PaginatedCourseListSchema:
        courses = await self.course_repository.find_public_courses_paginated(
            limit=limit,
            offset=offset,
            query=filters.q,
            sort=filters.sort,
        )
        total = await self.course_repository.count_public_courses(
            query=filters.q,
        )

        return PaginatedCourseListSchema(
            items=[
                CourseListItemSchema.model_validate(
                    course,
                    from_attributes=True,
                )
                for course in courses
            ],
            meta=PaginationSchema(total=total, limit=limit, offset=offset),
        )
