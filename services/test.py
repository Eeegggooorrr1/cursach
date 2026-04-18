import re
from dataclasses import dataclass

from pydantic import ValidationError

from ai.contracts import GeneratedTestSchema, LLMClient, \
   PreparedQuestionData
from ai.factories.test_generation_factory import TestGenerationPromptFactory
from core.exceptions import (
    InvalidGeneratedTestError,
    InvalidLLMResponseError,
    TestNotFoundError, CourseNotFoundError,
)
from repositories.course import CourseRepository
from repositories.course_progress import CourseProgressRepository
from repositories.subtopic import SubtopicRepository
from repositories.subtopic_progress import SubtopicProgressRepository
from repositories.test import TestRepository
from repositories.test_progress import TestProgressRepository
from schemas.test import TestReadSchema


@dataclass
class TestService:
    course_repository: CourseRepository
    course_progress_repository: CourseProgressRepository
    subtopic_progress_repository: SubtopicProgressRepository
    test_progress_repository: TestProgressRepository
    subtopic_repository: SubtopicRepository
    test_repository: TestRepository
    llm_client: LLMClient
    prompt_factory: TestGenerationPromptFactory

    async def create_test(self, course_id: int, user_id: int):
        course = await self.course_repository.get_course_by_id(course_id=course_id)
        if course is None:
            raise CourseNotFoundError()

        course_progress = await self.course_progress_repository.find_by_course_and_user(
            course_id=course_id,
            user_id=user_id,
        )
        if course_progress is None:
            await self.course_progress_repository.create(
                course_id=course_id,
                user_id=user_id,
                status="active",
            )

        subtopics = await self.subtopic_repository.find_by_course_id(course_id=course_id)
        if not subtopics:
            raise InvalidGeneratedTestError(message="Course has no subtopics")

        subtopic_ids = [subtopic.id for subtopic in subtopics]
        subtopic_progress_list = await self.subtopic_progress_repository.find_by_user_and_subtopic_ids(
            user_id=user_id,
            subtopic_ids=subtopic_ids,
        )
        subtopic_progress_by_id = {
            item.subtopic_id: item for item in subtopic_progress_list
        }

        next_position = await self.test_repository.get_next_position(course_id=course_id)

        prompt_subtopics = [
            {
                "name": subtopic.name,
                "difficulty": (
                    subtopic_progress_by_id[subtopic.id].current_difficulty
                    if subtopic.id in subtopic_progress_by_id
                    else 0
                ),
                "questions_count": 2,
            }
            for subtopic in subtopics
        ]

        recent_tests_questions = await self.test_progress_repository.get_last_questions(
            course_id=course_id,
            user_id=user_id,
            limit=3,
        )

        prompt = self.prompt_factory.build(
            course_title=course.title,
            course_comment=course.comment,
            test_no=next_position,
            subtopics=prompt_subtopics,
            recent_tests_questions=recent_tests_questions,
        )

        try:
            raw_answer = await self.llm_client.complete(
                system=prompt.system,
                user=prompt.user,
                temperature=0.0,
            )
        except Exception as exc:
            raise InvalidLLMResponseError(message="LLM request failed") from exc

        allowed_subtopic_names = {subtopic.name for subtopic in subtopics}
        subtopic_name_to_id = {subtopic.name: subtopic.id for subtopic in subtopics}
        questions_by_subtopic = {item["name"]: item["questions_count"] for item in prompt_subtopics}

        def normalize_text(text: str) -> str:
            return re.sub(r"\s+", " ", text).strip().casefold()

        recent_questions_normalized = {
            normalize_text(q) for q in recent_tests_questions
        }

        try:
            generated = GeneratedTestSchema.model_validate_json(
                raw_answer,
                context={
                    "questions_count": sum(questions_by_subtopic.values()),
                    "options_count": 3,
                    "allowed_subtopic_names": allowed_subtopic_names,
                    "questions_by_subtopic": questions_by_subtopic,
                    "recent_questions_normalized": recent_questions_normalized,
                },
            )
        except ValidationError as exc:
            raise InvalidLLMResponseError(
                message="LLM returned invalid JSON/schema"
            ) from exc

        prepared_questions = self._prepare_generated_test(
            generated=generated,
            subtopic_name_to_id=subtopic_name_to_id,
        )

        test = await self.test_repository.create_test(
            course_id=course_id,
            position=next_position,
            title=f"Тест {next_position}",
            questions=prepared_questions,
        )

        await self.test_progress_repository.create_in_progress(
            user_id=user_id,
            test_id=test.id,
        )

        full_test = await self.test_repository.get_test_with_details(test.id)
        if full_test is None:
            raise TestNotFoundError()

        return full_test

    @staticmethod
    def _prepare_generated_test(
        generated: GeneratedTestSchema,
        subtopic_name_to_id: dict[str, int],
    ) -> list[PreparedQuestionData]:
        prepared_questions: list[PreparedQuestionData] = []

        for question in generated.questions:
            prepared_questions.append(
                PreparedQuestionData(
                    subtopic_id=subtopic_name_to_id[question.subtopic],
                    prompt=question.text,
                    options=question.options,
                    correct_option_index=question.correct_option_index,
                )
            )

        return prepared_questions