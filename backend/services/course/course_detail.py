from dataclasses import dataclass

from core.exceptions import CourseNotFoundError
from models.user import RoleEnum
from repositories.course import CourseRepository
from repositories.subtopic import SubtopicRepository
from repositories.subtopic_progress import SubtopicProgressRepository
from repositories.test_progress import TestProgressRepository
from schemas.course import (
    CourseDetailSchema,
    CourseHistoryTestItemSchema,
    CourseProgressItemSchema,
    CourseProgressResponseSchema,
    PaginatedCourseDetailSchema,
    PaginationSchema,
)


@dataclass
class CourseDetailService:
    course_repository: CourseRepository
    test_progress_repository: TestProgressRepository
    subtopic_repository: SubtopicRepository
    subtopic_progress_repository: SubtopicProgressRepository

    async def get_course_detail(
        self,
        user_id: int,
        user_role: RoleEnum,
        course_id: int,
        limit: int,
        offset: int,
    ) -> PaginatedCourseDetailSchema:
        if user_role == RoleEnum.ADMIN:
            course = await self.course_repository.get_course_by_id(
                course_id=course_id,
            )
        else:
            course = await self.course_repository.find_by_id_and_user(
                course_id=course_id,
                user_id=user_id,
            )
        if course is None:
            raise CourseNotFoundError()

        link = await self.course_repository.find_user_course_link(
            user_id=user_id,
            course_id=course_id,
        )
        if link is None:
            rows = []
            total = 0
        else:
            rows = await self.test_progress_repository.get_course_history(
                user_id=user_id,
                course_id=course_id,
                limit=limit,
                offset=offset,
            )
            total = await self.test_progress_repository.count_course_history(
                user_id=user_id,
                course_id=course_id,
            )

        tests: list[CourseHistoryTestItemSchema] = []
        for test, progress in rows:
            is_finished = progress.status == "finished"
            tests.append(
                CourseHistoryTestItemSchema(
                    id=test.id,
                    position=test.position,
                    title=test.title,
                    status=progress.status,
                    correct_percentage=(
                        progress.correct_percentage if is_finished else 0.0
                    ),
                    error_percentage=(
                        round(100.0 - progress.correct_percentage, 2)
                        if is_finished
                        else 0.0
                    ),
                    started_at=progress.started_at,
                    finished_at=progress.finished_at,
                )
            )

        return PaginatedCourseDetailSchema(
            course=CourseDetailSchema.model_validate(
                course,
                from_attributes=True,
            ),
            tests=tests,
            meta=PaginationSchema(total=total, limit=limit, offset=offset),
        )

    async def get_course_progress(
        self,
        user_id: int,
        course_id: int,
    ) -> CourseProgressResponseSchema:
        course = await self.course_repository.find_by_id_and_user(
            course_id=course_id,
            user_id=user_id,
        )
        if course is None:
            raise CourseNotFoundError()

        topic_subtopic_rows = (
            await self.subtopic_repository.find_with_topics_by_course_id(
                course_id=course_id,
            )
        )

        subtopic_ids = [subtopic.id for _, subtopic in topic_subtopic_rows]
        progress_rows = await self.subtopic_progress_repository.find_by_user_and_subtopic_ids(
            user_id=user_id,
            subtopic_ids=subtopic_ids,
        )
        progress_by_subtopic_id = {
            row.subtopic_id: row for row in progress_rows
        }

        items: list[CourseProgressItemSchema] = []
        for topic, subtopic in topic_subtopic_rows:
            progress = progress_by_subtopic_id.get(subtopic.id)
            items.append(
                CourseProgressItemSchema(
                    topic_id=topic.id,
                    topic_name=topic.name,
                    subtopic_id=subtopic.id,
                    subtopic_name=subtopic.name,
                    mastery_score=progress.mastery_score if progress else 0.0,
                    current_difficulty=(
                        progress.current_difficulty if progress else 0
                    ),
                    current_streak=progress.current_streak if progress else 0,
                )
            )

        return CourseProgressResponseSchema(items=items)
