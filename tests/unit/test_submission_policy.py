import pytest

from core.enums import Difficulty
from core.exceptions import InvalidTestSubmissionError
from schemas.test import SubmitAnswerSchema
import schemas.test as test_schemas
import services.submission as submission_service
from tests.factories import (
    make_answer_option,
    make_question,
    make_subtopic_progress,
    make_test,
)


def test_multiple_choice_partial_answer_is_wrong() -> None:
    question = make_question(
        1,
        is_multiple_choice=True,
        options=[
            make_answer_option(10, is_correct=True),
            make_answer_option(11, is_correct=True),
            make_answer_option(12, is_correct=False),
        ],
    )
    test = make_test([question])

    result = submission_service.TestSubmissionPolicy().evaluate(
        test=test,
        submitted_answers=[
            SubmitAnswerSchema(question_id=1, selected_option_ids=[10])
        ],
        current_progress_by_subtopic_id={},
    )

    assert result.correct_count == 0
    assert result.incorrect_count == 1
    assert result.attempts[0].is_correct is False


def test_hard_difficulty_does_not_demote_after_all_correct() -> None:
    question = make_question(
        1,
        subtopic_id=7,
        options=[
            make_answer_option(10, is_correct=True),
            make_answer_option(11, is_correct=False),
        ],
    )
    test = make_test([question])
    progress = make_subtopic_progress(
        7,
        mastery_score=0.30,
        current_difficulty=Difficulty.HARD,
    )

    result = submission_service.TestSubmissionPolicy().evaluate(
        test=test,
        submitted_answers=[
            SubmitAnswerSchema(question_id=1, selected_option_ids=[10])
        ],
        current_progress_by_subtopic_id={7: progress},
    )

    assert result.correct_count == 1
    assert result.subtopic_updates[0].current_difficulty == int(
        Difficulty.HARD
    )


def test_single_choice_requires_exactly_one_selected_option() -> None:
    question = make_question(
        1,
        is_multiple_choice=False,
        options=[
            make_answer_option(10, is_correct=True),
            make_answer_option(11, is_correct=False),
        ],
    )
    test = make_test([question])
    payload = test_schemas.TestSubmitSchema(
        answers=[
            SubmitAnswerSchema(
                question_id=1,
                selected_option_ids=[10, 11],
            )
        ]
    )

    with pytest.raises(InvalidTestSubmissionError):
        submission_service.TestSubmissionService._validate_payload_against_test(
            test=test,
            payload=payload,
        )
