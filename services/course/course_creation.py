import logging
from dataclasses import dataclass

from pydantic import ValidationError

from ai.contracts import LLMClient
from ai.factories.course_generation_factory import (
    CourseGenerationPromptFactory,
)
from ai.schemas import GeneratedCourseStructureSchema, normalize_text
from core.enums import Difficulty
from core.exceptions import (
    InvalidCourseStructureError,
    InvalidLLMResponseError,
)
from repositories.course import CourseRepository
from services.course.course_support import (
    CourseCacheInvalidationService,
    CourseLearningStateService,
)
from services.course.policies import CourseGenerationPolicy


logger = logging.getLogger(__name__)


@dataclass
class CourseCreationService:
    course_repository: CourseRepository
    llm_client: LLMClient
    prompt_factory: CourseGenerationPromptFactory
    course_policy: CourseGenerationPolicy
    learning_state_service: CourseLearningStateService
    cache_invalidation_service: CourseCacheInvalidationService

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

        await self.learning_state_service.ensure_learning_state(
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
        if full_course.is_public:
            await self.cache_invalidation_service.invalidate_public_courses_cache()
        return full_course

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
