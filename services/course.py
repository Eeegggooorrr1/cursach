from dataclasses import dataclass

from pydantic import ValidationError

from ai.contracts import GeneratedCourseStructureSchema, LLMClient
from ai.factories.course_generation_factory import (
    CourseGenerationPromptFactory,
)
from core.exceptions import (
    InvalidCourseStructureError,
    InvalidLLMResponseError,
    CourseNotFoundError,
)
from repositories.course import CourseRepository
from repositories.subtopic import SubtopicRepository
from repositories.subtopic_progress import SubtopicProgressRepository
from repositories.test_progress import TestProgressRepository
from schemas.course import (
    PaginatedCourseListSchema,
    CourseListItemSchema,
    PaginationSchema,
    PaginatedCourseDetailSchema,
    CourseHistoryTestItemSchema,
    CourseDetailSchema,
    CourseProgressResponseSchema,
    CourseProgressItemSchema,
)


@dataclass(frozen=True)
class CourseGenerationPolicy:
    @staticmethod
    def get_subtopics_count(topics_count: int) -> int:
        if topics_count == 1:
            return 8
        if topics_count == 2:
            return 4
        if 3 <= topics_count <= 5:
            return 3
        return 2


@dataclass
class CourseService:
    course_repository: CourseRepository
    llm_client: LLMClient
    prompt_factory: CourseGenerationPromptFactory
    course_policy: CourseGenerationPolicy
    test_progress_repository: TestProgressRepository
    subtopic_repository: SubtopicRepository
    subtopic_progress_repository: SubtopicProgressRepository

    async def create_course(
        self,
        user_id: int,
        title: str,
        comment: str | None,
        topics: list[str],
    ):

        course = await self.course_repository.create_course(
            user_id=user_id,
            title=title,
            comment=comment,
        )

        subtopics_count = self.course_policy.get_subtopics_count(len(topics))

        prompt = self.prompt_factory.build(
            title=title,
            comment=comment,
            topics=topics,
            subtopics_count=subtopics_count,
        )

        try:
            raw_answer = await self.llm_client.complete(
                system=prompt.system,
                user=prompt.user,
                temperature=0.0,
            )
        except Exception as exc:
            raise InvalidLLMResponseError() from exc

        try:
            generated = GeneratedCourseStructureSchema.model_validate_json(
                raw_answer
            )
        except ValidationError as exc:
            raise InvalidLLMResponseError() from exc

        self._validate_generated_course(
            expected_topics=topics,
            expected_subtopics_count=subtopics_count,
            generated=generated,
        )

        await self.course_repository.save_generated_course(
            course_id=course.id,
            generated=generated,
        )

        full_course = await self.course_repository.get_course_with_details(
            course.id
        )
        if not full_course:
            raise InvalidCourseStructureError("Course not found after save")

        return full_course

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

        return PaginatedCourseListSchema(
            items=[
                CourseListItemSchema.model_validate(
                    course, from_attributes=True
                )
                for course in courses
            ],
            meta=PaginationSchema(total=total, limit=limit, offset=offset),
        )

    async def get_course_detail(
        self,
        user_id: int,
        course_id: int,
        limit: int,
        offset: int,
    ) -> PaginatedCourseDetailSchema:
        course = await self.course_repository.find_by_id_and_user(
            course_id=course_id,
            user_id=user_id,
        )
        if course is None:
            raise CourseNotFoundError()

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
            tests.append(
                CourseHistoryTestItemSchema(
                    id=test.id,
                    position=test.position,
                    title=test.title,
                    status=progress.status,
                    correct_percentage=progress.correct_percentage,
                    error_percentage=round(
                        100.0 - progress.correct_percentage, 2
                    ),
                    started_at=progress.started_at,
                    finished_at=progress.finished_at,
                )
            )

        return PaginatedCourseDetailSchema(
            course=CourseDetailSchema.model_validate(
                course, from_attributes=True
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

    @staticmethod
    def _validate_generated_course(
        expected_topics: list[str],
        expected_subtopics_count: int,
        generated: GeneratedCourseStructureSchema,
    ) -> None:
        expected = [
            topic.strip() for topic in expected_topics if topic.strip()
        ]
        actual = [topic.name for topic in generated.topics]

        if len(actual) != len(expected):
            raise InvalidCourseStructureError(
                "LLM returned wrong number of topics"
            )

        if set(expected) != set(actual):
            raise InvalidCourseStructureError(
                "LLM returned topics that do not match requested topics"
            )

        for topic in generated.topics:
            if len(topic.subtopics) != expected_subtopics_count:
                raise InvalidCourseStructureError(
                    f"Topic '{topic.name}' must contain exactly {expected_subtopics_count} subtopics",
                )
