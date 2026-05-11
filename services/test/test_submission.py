import logging
from dataclasses import dataclass

from core.exceptions import TestNotFoundError, \
    InvalidTestSubmissionError, TestAlreadySubmittedError
from models.progress import TestProgressStatusEnum
from models.test import Test
from repositories.course_progress import CourseProgressRepository
from repositories.question_attempt import QuestionAttemptRepository
from repositories.subtopic_progress import SubtopicProgressRepository
from repositories.test import TestRepository
from repositories.test_progress import TestProgressRepository
from services.test.policies import TestSubmissionPolicy
from schemas.test import (
    TestSubmitResponseSchema,
    TestSubmitSchema,
)


logger = logging.getLogger(__name__)


@dataclass
class TestSubmissionService:
    course_progress_repository: CourseProgressRepository
    test_repository: TestRepository
    test_progress_repository: TestProgressRepository
    question_attempt_repository: QuestionAttemptRepository
    subtopic_progress_repository: SubtopicProgressRepository
    submission_policy: TestSubmissionPolicy

    async def submit_test(
        self,
        course_id: int,
        test_id: int,
        user_id: int,
        payload: TestSubmitSchema,
    ) -> TestSubmitResponseSchema:

        test = await self.test_repository.get_test_with_details(
            test_id=test_id
        )
        if (
            test is None
            or test.course_id != course_id
            or test.user_id != user_id
        ):
            raise TestNotFoundError()

        test_progress = await self.test_progress_repository.find_for_update_by_user_and_test(
            user_id=user_id,
            test_id=test_id,
        )
        if test_progress is None:
            raise InvalidTestSubmissionError("test progress not found")

        if test_progress.status == TestProgressStatusEnum.FINISHED:
            raise TestAlreadySubmittedError()

        self._validate_payload_against_test(test=test, payload=payload)

        subtopic_ids = {question.subtopic_id for question in test.questions}
        current_progresses = await self.subtopic_progress_repository.find_by_user_and_subtopic_ids(
            user_id=user_id,
            subtopic_ids=list(subtopic_ids),
        )
        current_progress_by_id = {
            item.subtopic_id: item for item in current_progresses
        }

        evaluation = self.submission_policy.evaluate(
            test=test,
            submitted_answers=payload.answers,
            current_progress_by_subtopic_id=current_progress_by_id,
        )

        await self.question_attempt_repository.bulk_create(
            test_progress_id=test_progress.id,
            attempts=evaluation.attempts,
        )

        total_questions = len(test.questions)
        correct_percentage = round(
            (evaluation.correct_count / total_questions) * 100.0, 2
        )

        await self.test_progress_repository.mark_finished(
            test_progress,
            correct_percentage=correct_percentage,
        )

        await self.subtopic_progress_repository.upsert_many(
            user_id=user_id,
            updates=evaluation.subtopic_updates,
        )

        logger.info(
            "Test submitted: user_id=%s course_id=%s test_id=%s correct=%s incorrect=%s correct_percentage=%s",
            user_id,
            course_id,
            test.id,
            evaluation.correct_count,
            evaluation.incorrect_count,
            correct_percentage,
        )

        return TestSubmitResponseSchema(
            test_progress_id=test_progress.id,
            test_id=test.id,
            status=TestProgressStatusEnum.FINISHED,
            correct_percentage=correct_percentage,
        )

    @staticmethod
    def _validate_payload_against_test(
        test: Test,
        payload: TestSubmitSchema
    ) -> None:
        expected_question_ids = {question.id for question in test.questions}
        submitted_question_ids = {
            answer.question_id for answer in payload.answers
        }

        if submitted_question_ids != expected_question_ids:
            raise InvalidTestSubmissionError(
                "submitted answers do not match test questions"
            )

        answers_by_question_id = {
            answer.question_id: answer for answer in payload.answers
        }

        for question in test.questions:
            answer = answers_by_question_id[question.id]
            valid_option_ids = {
                option.id for option in question.answer_options
            }
            selected_option_ids = set(answer.selected_option_ids)

            if not selected_option_ids.issubset(valid_option_ids):
                raise InvalidTestSubmissionError(
                    f"selected option does not belong to question_id={question.id}"
                )

            if not question.is_multiple_choice and len(selected_option_ids) != 1:
                raise InvalidTestSubmissionError(
                    f"single choice question_id={question.id} requires exactly one selected option"
                )
