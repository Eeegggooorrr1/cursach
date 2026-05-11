from models.course import Subtopic
from models.progress import SubtopicProgress
from models.test import AnswerOption, Question, Test


def make_answer_option(
    option_id: int,
    *,
    is_correct: bool,
    text: str | None = None,
    position: int | None = None,
) -> AnswerOption:
    return AnswerOption(
        id=option_id,
        text=text or f"Option {option_id}",
        is_correct=is_correct,
        position=position if position is not None else option_id,
    )


def make_question(
    question_id: int,
    *,
    subtopic_id: int = 1,
    is_multiple_choice: bool = False,
    options: list[AnswerOption] | None = None,
) -> Question:
    return Question(
        id=question_id,
        subtopic_id=subtopic_id,
        prompt=f"Question {question_id}",
        is_multiple_choice=is_multiple_choice,
        position=question_id,
        answer_options=options or [
            make_answer_option(1, is_correct=True),
            make_answer_option(2, is_correct=False),
        ],
    )


def make_test(
    questions: list[Question],
    *,
    test_id: int = 1,
    course_id: int = 1,
    user_id: int = 1,
) -> Test:
    return Test(
        id=test_id,
        course_id=course_id,
        user_id=user_id,
        title="Test",
        position=1,
        questions=questions,
    )


def make_subtopic(subtopic_id: int, name: str | None = None) -> Subtopic:
    return Subtopic(id=subtopic_id, name=name or f"Subtopic {subtopic_id}")


def make_subtopic_progress(
    subtopic_id: int,
    *,
    mastery_score: float,
    current_difficulty: int,
    current_streak: int = 0,
    user_id: int = 1,
) -> SubtopicProgress:
    return SubtopicProgress(
        user_id=user_id,
        subtopic_id=subtopic_id,
        mastery_score=mastery_score,
        current_difficulty=current_difficulty,
        current_streak=current_streak,
    )
