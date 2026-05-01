import logging
from dataclasses import dataclass

from core.dto import (
    QuestionAttemptDraft,
    SubmissionEvaluationResult,
    SubtopicProgressUpdate,
)
from core.enums import Difficulty
from core.exceptions import TestNotFoundError, \
    InvalidTestSubmissionError, TestAlreadySubmittedError
from models.progress import SubtopicProgress, TestProgressStatusEnum
from models.test import Test
from repositories.course_progress import CourseProgressRepository
from repositories.question_attempt import QuestionAttemptRepository
from repositories.subtopic_progress import SubtopicProgressRepository
from repositories.test import TestRepository
from repositories.test_progress import TestProgressRepository
from schemas.test import (
    SubmitAnswerSchema,
    TestSubmitResponseSchema,
    TestSubmitSchema,
)


logger = logging.getLogger(__name__)


class TestSubmissionPolicy:
    CORRECT_GAIN = {
        Difficulty.EASY: 0.04,
        Difficulty.MEDIUM: 0.05,
        Difficulty.HARD: 0.06,
    }
    WRONG_PENALTY = {
        Difficulty.EASY: 0.05,
        Difficulty.MEDIUM: 0.06,
        Difficulty.HARD: 0.07,
    }

    PROMOTE_THRESHOLD = {
        Difficulty.EASY: 0.20,
        Difficulty.MEDIUM: 0.45,
    }
    DEMOTE_THRESHOLD = {
        Difficulty.MEDIUM: 0.12,
        Difficulty.HARD: 0.28,
    }

    def evaluate(
        self,
        test: Test,
        submitted_answers: list[SubmitAnswerSchema],
        current_progress_by_subtopic_id: dict[int, SubtopicProgress],
    ) -> SubmissionEvaluationResult:
        answers_by_question_id = {
            item.question_id: item for item in submitted_answers
        }

        attempts: list[QuestionAttemptDraft] = []
        correct_count = 0
        incorrect_count = 0

        per_subtopic_correct: dict[int, int] = {}
        per_subtopic_total: dict[int, int] = {}
        per_subtopic_wrong: dict[int, int] = {}

        for question in test.questions:
            answer = answers_by_question_id[question.id]
            selected_option_ids = set(answer.selected_option_ids)
            correct_option_ids = {
                option.id
                for option in question.answer_options
                if option.is_correct
            }
            is_correct = selected_option_ids == correct_option_ids

            attempts.append(
                QuestionAttemptDraft(
                    question_id=question.id,
                    selected_option_ids=answer.selected_option_ids,
                    is_correct=is_correct,
                )
            )

            subtopic_id = question.subtopic_id
            per_subtopic_total[subtopic_id] = (
                per_subtopic_total.get(subtopic_id, 0) + 1
            )
            if is_correct:
                correct_count += 1
                per_subtopic_correct[subtopic_id] = (
                    per_subtopic_correct.get(subtopic_id, 0) + 1
                )
            else:
                incorrect_count += 1
                per_subtopic_wrong[subtopic_id] = (
                    per_subtopic_wrong.get(subtopic_id, 0) + 1
                )

        subtopic_updates: list[SubtopicProgressUpdate] = []

        for subtopic_id in per_subtopic_total.keys():
            progress = current_progress_by_subtopic_id.get(subtopic_id)

            old_score = progress.mastery_score if progress is not None else 0.0
            old_difficulty_value = (
                progress.current_difficulty
                if progress is not None
                else Difficulty.EASY
            )
            old_streak = progress.current_streak if progress is not None else 0

            try:
                old_difficulty = Difficulty(old_difficulty_value)
            except ValueError:
                old_difficulty = Difficulty.EASY

            good = per_subtopic_correct.get(subtopic_id, 0)
            bad = per_subtopic_wrong.get(subtopic_id, 0)
            total = per_subtopic_total[subtopic_id]

            score_delta = (
                good * self.CORRECT_GAIN[old_difficulty]
                - bad * self.WRONG_PENALTY[old_difficulty]
            )
            new_score = self._clamp(old_score + score_delta, 0.0, 1.0)

            all_correct_for_subtopic = bad == 0 and total > 0
            new_streak = old_streak + 1 if all_correct_for_subtopic else 0

            new_difficulty = self._resolve_new_difficulty(
                current=old_difficulty,
                mastery_score=new_score,
                streak=new_streak,
                had_errors=bad > 0,
            )

            subtopic_updates.append(
                SubtopicProgressUpdate(
                    subtopic_id=subtopic_id,
                    mastery_score=new_score,
                    current_difficulty=int(new_difficulty),
                    current_streak=new_streak,
                )
            )

        return SubmissionEvaluationResult(
            attempts=attempts,
            subtopic_updates=subtopic_updates,
            correct_count=correct_count,
            incorrect_count=incorrect_count,
        )

    def _resolve_new_difficulty(
        self,
        current: Difficulty,
        mastery_score: float,
        streak: int,
        had_errors: bool,
    ) -> Difficulty:
        if current == Difficulty.EASY:
            if (
                streak > 0
                and streak % 3 == 0
                and mastery_score >= self.PROMOTE_THRESHOLD[Difficulty.EASY]
            ):
                return Difficulty.MEDIUM
            return Difficulty.EASY

        if current == Difficulty.MEDIUM:
            if (
                had_errors
                and mastery_score < self.DEMOTE_THRESHOLD[Difficulty.MEDIUM]
            ):
                return Difficulty.EASY
            if (
                streak > 0
                and streak % 3 == 0
                and mastery_score >= self.PROMOTE_THRESHOLD[Difficulty.MEDIUM]
            ):
                return Difficulty.HARD
            return Difficulty.MEDIUM

        if (
            had_errors
            and mastery_score < self.DEMOTE_THRESHOLD[Difficulty.HARD]
        ):
            return Difficulty.MEDIUM
        return Difficulty.HARD

    @staticmethod
    def _clamp(value: float, low: float, high: float) -> float:
        return max(low, min(high, value))


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
                    f"selected_option_id does not belong to question_id={question.id}"
                )

            if not question.is_multiple_choice and len(selected_option_ids) != 1:
                raise InvalidTestSubmissionError(
                    f"single choice question_id={question.id} requires exactly one selected option"
                )
