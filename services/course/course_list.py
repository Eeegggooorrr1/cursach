from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from repositories.course import CourseRepository
from repositories.test_progress import TestProgressRepository
from schemas.course import (
    CourseDashboardSummarySchema,
    CourseListItemSchema,
    DashboardLastTestSchema,
    PaginatedCourseListSchema,
    PaginationSchema,
)


@dataclass
class CourseListService:
    course_repository: CourseRepository
    test_progress_repository: TestProgressRepository

    async def get_user_courses(
        self,
        user_id: int,
        limit: int,
        offset: int,
    ) -> PaginatedCourseListSchema:
        courses = await self.course_repository.find_user_courses_paginated(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        total = await self.course_repository.count_user_courses(
            user_id=user_id
        )

        return self._build_course_list_response(
            courses=courses,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_dashboard_summary(
        self,
        user_id: int,
    ) -> CourseDashboardSummarySchema:
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        active_courses = await self.course_repository.count_user_courses(
            user_id=user_id
        )
        shared_courses = (
            await self.course_repository.count_shared_user_courses(
                user_id=user_id
            )
        )
        public_courses = (
            await self.course_repository.count_public_user_courses(
                user_id=user_id
            )
        )
        tests_last_week = await self.test_progress_repository.count_started_since(
            user_id=user_id,
            since=one_week_ago,
        )
        last_test_row = await self.test_progress_repository.get_last_finished_summary(
            user_id=user_id
        )

        last_test = None
        if last_test_row is not None:
            last_test = DashboardLastTestSchema(
                course_id=last_test_row.course_id,
                test_id=last_test_row.test_id,
                course_title=last_test_row.course_title,
                test_title=last_test_row.test_title,
                questions_count=last_test_row.questions_count,
                incorrect_answers_count=(
                    last_test_row.questions_count
                    - last_test_row.correct_answers_count
                ),
                correct_percentage=last_test_row.correct_percentage,
                started_at=last_test_row.started_at,
                finished_at=last_test_row.finished_at,
            )

        return CourseDashboardSummarySchema(
            active_courses=active_courses,
            tests_last_week=tests_last_week,
            shared_courses=shared_courses,
            public_courses=public_courses,
            last_test=last_test,
        )

    async def get_public_courses(
        self,
        limit: int,
        offset: int,
    ) -> PaginatedCourseListSchema:
        courses = await self.course_repository.find_public_courses_paginated(
            limit=limit,
            offset=offset,
        )
        total = await self.course_repository.count_public_courses()
        return self._build_course_list_response(
            courses=courses,
            total=total,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def _build_course_list_response(
        courses,
        total: int,
        limit: int,
        offset: int,
    ) -> PaginatedCourseListSchema:
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
