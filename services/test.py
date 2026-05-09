import logging
import re
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from ai.schemas import GeneratedTestSchema
from ai.contracts import LLMClient
from ai.factories.test_generation_factory import TestGenerationPromptFactory
from core.dto import PreparedQuestionData
from core.exceptions import (
    CourseNotFoundError,
    InvalidGeneratedTestError,
    InvalidLLMResponseError,
    TestNotFoundError,
    TestReviewNotAvailableError,
)
from models.progress import CourseProgressStatusEnum, TestProgressStatusEnum
from models.course import Subtopic
from models.progress import SubtopicProgress
from repositories.course import CourseRepository
from repositories.course_progress import CourseProgressRepository
from repositories.question_attempt import QuestionAttemptRepository
from repositories.subtopic import SubtopicRepository
from repositories.subtopic_progress import SubtopicProgressRepository
from repositories.test import TestRepository
from repositories.test_progress import TestProgressRepository
from schemas.course import (
    ReviewAttemptSchema,
    ReviewTestSchema,
    TestReviewResponseSchema,
)


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TestQuestionCountPolicy:
    min_questions: int = 10
    max_questions: int = 24

    def build_subtopic_plan(
        self,
        subtopics: list[Subtopic],
        progress_by_subtopic_id: dict[int, SubtopicProgress],
        test_no: int,
    ) -> list[dict[str, Any]]:
        if not subtopics:
            return []

        selected_subtopics = self._select_subtopics(
            subtopics=subtopics,
            test_no=test_no,
        )
        total_questions = min(
            self.max_questions,
            max(self.min_questions, len(selected_subtopics)),
        )
        extra_questions = total_questions - len(selected_subtopics)

        plan = [
            {
                "name": subtopic.name,
                "difficulty": self._difficulty_for(
                    subtopic=subtopic,
                    progress_by_subtopic_id=progress_by_subtopic_id,
                ),
                "questions_count": 1,
            }
            for subtopic in selected_subtopics
        ]

        weighted_indexes = sorted(
            range(len(plan)),
            key=lambda index: (-plan[index]["difficulty"], index),
        )
        for index in range(extra_questions):
            plan[weighted_indexes[index % len(weighted_indexes)]][
                "questions_count"
            ] += 1

        return plan

    def _select_subtopics(
        self,
        subtopics: list[Subtopic],
        test_no: int,
    ) -> list[Subtopic]:
        if len(subtopics) <= self.max_questions:
            return subtopics

        start = ((test_no - 1) * self.max_questions) % len(subtopics)
        rotated = subtopics[start:] + subtopics[:start]
        return rotated[: self.max_questions]

    @staticmethod
    def _difficulty_for(
        subtopic: Subtopic,
        progress_by_subtopic_id: dict[int, SubtopicProgress],
    ) -> int:
        progress = progress_by_subtopic_id.get(subtopic.id)
        return progress.current_difficulty if progress is not None else 0


@dataclass
class TestService:
    course_repository: CourseRepository
    course_progress_repository: CourseProgressRepository
    subtopic_progress_repository: SubtopicProgressRepository
    test_progress_repository: TestProgressRepository
    subtopic_repository: SubtopicRepository
    test_repository: TestRepository
    question_attempt_repository: QuestionAttemptRepository
    llm_client: LLMClient
    prompt_factory: TestGenerationPromptFactory
    question_count_policy: TestQuestionCountPolicy

    async def create_test(self, course_id: int, user_id: int):
        course = await self.course_repository.find_by_id_and_user(
            course_id=course_id,
            user_id=user_id,
        )
        if course is None:
            raise CourseNotFoundError()

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
            course_id=course_id
        )
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

        next_position = await self.test_repository.get_next_position(
            course_id=course_id,
            user_id=user_id,
        )

        prompt_subtopics = self.question_count_policy.build_subtopic_plan(
            subtopics=subtopics,
            progress_by_subtopic_id=subtopic_progress_by_id,
            test_no=next_position,
        )
        planned_questions_count = sum(
            item["questions_count"] for item in prompt_subtopics
        )
        logger.info(
            "Generating test: user_id=%s course_id=%s test_position=%s subtopics=%s questions=%s",
            user_id,
            course_id,
            next_position,
            len(prompt_subtopics),
            planned_questions_count,
        )

        recent_tests_questions = (
            await self.test_progress_repository.get_last_questions(
                course_id=course_id,
                user_id=user_id,
                limit=1,
            )
        )

        prompt = self.prompt_factory.build(
            course_title=course.title,
            course_prompt=course.prompt,
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
            logger.warning(
                "Test generation LLM request failed: user_id=%s course_id=%s test_position=%s",
                user_id,
                course_id,
                next_position,
            )
            raise InvalidLLMResponseError(
                message="LLM request failed"
            ) from exc

        allowed_subtopic_names = {subtopic.name for subtopic in subtopics}
        subtopic_name_to_id = {
            self._normalize_text(subtopic.name): subtopic.id
            for subtopic in subtopics
        }
        questions_by_subtopic = {
            item["name"]: item["questions_count"]
            for item in prompt_subtopics
        }
        recent_questions_normalized = {
            self._normalize_text(q) for q in recent_tests_questions
        }

        try:
            generated = GeneratedTestSchema.model_validate_json(
                raw_answer,
                context={
                    "questions_count": sum(questions_by_subtopic.values()),
                    "single_choice_options_range": (2, 6),
                    "multiple_choice_options_range": (3, 9),
                    "allowed_subtopic_names": allowed_subtopic_names,
                    "questions_by_subtopic": questions_by_subtopic,
                    "recent_questions_normalized": recent_questions_normalized,
                },
            )
        except ValidationError as exc:
            logger.warning(
                "Test generation returned invalid schema: user_id=%s course_id=%s test_position=%s",
                user_id,
                course_id,
                next_position,
            )
            raise InvalidLLMResponseError(
                message="LLM returned invalid JSON/schema"
            ) from exc

        prepared_questions = self._prepare_generated_test(
            generated=generated,
            subtopic_name_to_id=subtopic_name_to_id,
        )

        test = await self.test_repository.create_test(
            course_id=course_id,
            user_id=user_id,
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

        multiple_choice_count = sum(
            1 for question in full_test.questions if question.is_multiple_choice
        )
        logger.info(
            "Test created: user_id=%s course_id=%s test_id=%s questions=%s multiple_choice=%s",
            user_id,
            course_id,
            full_test.id,
            len(full_test.questions),
            multiple_choice_count,
        )
        return full_test

    async def get_test(
        self,
        course_id: int,
        test_id: int,
        user_id: int,
    ):
        test = await self.test_repository.get_test_with_details(test_id=test_id)
        if (
            test is None
            or test.course_id != course_id
            or test.user_id != user_id
        ):
            raise TestNotFoundError()
        return test

    async def get_review(
        self,
        user_id: int,
        course_id: int,
        test_id: int,
    ) -> TestReviewResponseSchema:
        test = await self.test_repository.get_test_with_details(
            test_id=test_id
        )
        if (
            test is None
            or test.course_id != course_id
            or test.user_id != user_id
        ):
            raise TestNotFoundError()

        progress = await self.test_progress_repository.find_by_user_and_test(
            user_id=user_id,
            test_id=test_id,
        )
        if (
            progress is None
            or progress.status != TestProgressStatusEnum.FINISHED
        ):
            raise TestReviewNotAvailableError()

        attempts = (
            await self.question_attempt_repository.find_by_test_progress_id(
                test_progress_id=progress.id,
            )
        )

        return TestReviewResponseSchema(
            test=ReviewTestSchema.from_orm_test(test),
            attempts=[
                ReviewAttemptSchema(
                    question_id=attempt.question_id,
                    selected_option_ids=self._selected_option_ids(attempt),
                    is_correct=attempt.is_correct,
                )
                for attempt in attempts
            ],
        )

    @staticmethod
    def _prepare_generated_test(
        generated: GeneratedTestSchema,
        subtopic_name_to_id: dict[str, int],
    ) -> list[PreparedQuestionData]:
        prepared_questions: list[PreparedQuestionData] = []

        for question in generated.questions:
            subtopic_key = TestService._normalize_text(question.subtopic)
            prepared_questions.append(
                PreparedQuestionData(
                    subtopic_id=subtopic_name_to_id[subtopic_key],
                    prompt=question.text,
                    options=question.options,
                    correct_option_indexes=question.correct_option_indexes,
                    is_multiple_choice=(
                        question.question_type == "multiple_choice"
                    ),
                )
            )

        return prepared_questions

    @staticmethod
    def _selected_option_ids(attempt) -> list[int]:
        return sorted(
            item.answer_option_id for item in attempt.selected_options
        )

    @staticmethod
    def _normalize_text(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip().casefold()
