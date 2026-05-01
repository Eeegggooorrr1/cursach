import logging
from dataclasses import dataclass

from pydantic import ValidationError

from ai.schemas import GeneratedCourseStructureSchema, normalize_text
from ai.contracts import LLMClient
from ai.factories.course_generation_factory import (
    CourseGenerationPromptFactory,
)
from core.dto import SubtopicProgressUpdate
from core.enums import Difficulty
from core.exceptions import (
    CourseNotFoundError,
    InvalidCourseStructureError,
    InvalidLLMResponseError,
)
from models.progress import CourseProgressStatusEnum
from repositories.course import CourseRepository
from repositories.course_progress import CourseProgressRepository
from repositories.subtopic import SubtopicRepository
from repositories.subtopic_progress import SubtopicProgressRepository
from repositories.test_progress import TestProgressRepository
from schemas.course import (
    CourseDetailSchema,
    CourseEnrollmentResponseSchema,
    CourseHistoryTestItemSchema,
    CourseListItemSchema,
    CourseProgressItemSchema,
    CourseProgressResponseSchema,
    PaginatedCourseDetailSchema,
    PaginatedCourseListSchema,
    PaginationSchema,
    PublicCourseDetailSchema,
)


logger = logging.getLogger(__name__)


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
    course_progress_repository: CourseProgressRepository
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
        prompt: str | None,
        topics: list[str],
        initial_difficulty: Difficulty,
        is_public: bool,
    ):
        logger.info(
            "Creating course: user_id=%s title=%s topics_count=%s initial_difficulty=%s is_public=%s",
            user_id,
            title,
            len(topics),
            int(initial_difficulty),
            is_public,
        )

        course = await self.course_repository.create_course(
            creator_id=user_id,
            title=title,
            comment=comment,
            prompt=prompt,
            is_public=is_public,
        )

        subtopics_count = self.course_policy.get_subtopics_count(len(topics))

        generation_prompt = self.prompt_factory.build(
            title=title,
            prompt=prompt,
            topics=topics,
            subtopics_count=subtopics_count,
        )

        try:
            raw_answer = await self.llm_client.complete(
                system=generation_prompt.system,
                user=generation_prompt.user,
                temperature=0.0,
            )
        except Exception as exc:
            logger.warning(
                "Course generation LLM request failed: user_id=%s course_id=%s",
                user_id,
                course.id,
            )
            raise InvalidLLMResponseError() from exc

        try:
            generated = GeneratedCourseStructureSchema.model_validate_json(
                raw_answer
            )
        except ValidationError as exc:
            logger.warning(
                "Course generation returned invalid schema: user_id=%s course_id=%s",
                user_id,
                course.id,
            )
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

        await self._ensure_learning_state(
            user_id=user_id,
            course_id=course.id,
            initial_difficulty=initial_difficulty,
        )

        full_course = await self.course_repository.get_course_with_details(
            course.id
        )
        if not full_course:
            raise InvalidCourseStructureError("Course not found after save")

        logger.info(
            "Course created: user_id=%s course_id=%s topics=%s",
            user_id,
            full_course.id,
            len(full_course.topics),
        )
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

        return self._build_course_list_response(
            courses=courses,
            total=total,
            limit=limit,
            offset=offset,
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

    async def get_public_course_detail(
        self,
        course_id: int,
    ) -> PublicCourseDetailSchema:
        course = await self.course_repository.find_public_with_details(
            course_id=course_id,
        )
        if course is None:
            raise CourseNotFoundError()

        return PublicCourseDetailSchema.model_validate(
            course,
            from_attributes=True,
        )

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

        await self._ensure_learning_state(
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
        return CourseDetailSchema.model_validate(
            course,
            from_attributes=True,
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

    async def _ensure_learning_state(
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

    @staticmethod
    def _validate_generated_course(
        expected_topics: list[str],
        expected_subtopics_count: int,
        generated: GeneratedCourseStructureSchema,
    ) -> None:
        expected = [
            normalize_text(topic).casefold()
            for topic in expected_topics
            if topic.strip()
        ]
        actual = [
            normalize_text(topic.name).casefold()
            for topic in generated.topics
        ]

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
