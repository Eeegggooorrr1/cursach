from dataclasses import dataclass

from pydantic import ValidationError

from ai.contracts import GeneratedCourseStructureSchema, LLMClient
from ai.factories.course_generation_factory import CourseGenerationPromptFactory
from core.exceptions import InvalidCourseStructureError, InvalidLLMResponseError
from repositories.course import CourseRepository


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

    async def create_course(
        self,
        user_id: int,
        title: str,
        comment: str | None,
        topics: list[str],
    ):

        # TODO: занести сложности подтем в subtopic_progress,
        #  занести режим в курс, при проверке не менять метрики, если режим статичный

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
            generated = GeneratedCourseStructureSchema.model_validate_json(raw_answer)
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

        full_course = await self.course_repository.get_course_with_details(course.id)
        if not full_course:
            raise InvalidCourseStructureError("Course not found after save")

        return full_course

    @staticmethod
    def _validate_generated_course(
        expected_topics: list[str],
        expected_subtopics_count: int,
        generated: GeneratedCourseStructureSchema,
    ) -> None:
        expected = [topic.strip() for topic in expected_topics if topic.strip()]
        actual = [topic.name for topic in generated.topics]

        if len(actual) != len(expected):
            raise InvalidCourseStructureError("LLM returned wrong number of topics")

        if set(expected) != set(actual):
            raise InvalidCourseStructureError("LLM returned topics that do not match requested topics")

        for topic in generated.topics:
            if len(topic.subtopics) != expected_subtopics_count:
                raise InvalidCourseStructureError(
                    f"Topic '{topic.name}' must contain exactly {expected_subtopics_count} subtopics",
                )