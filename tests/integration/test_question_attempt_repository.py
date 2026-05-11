import pytest
from sqlalchemy import select

from core.dto import QuestionAttemptDraft
from models.progress import QuestionAttemptSelectedOption
from repositories.question_attempt import QuestionAttemptRepository
from tests.conftest import (
    add_course_structure,
    create_course,
    create_test_with_questions,
    create_user,
)


pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_attempt_selected_options_are_persisted_in_link_table(
    db_session,
) -> None:
    user = await create_user(db_session)
    course = await create_course(db_session, creator=user)
    subtopic = await add_course_structure(db_session, course)
    _, question, options, progress = await create_test_with_questions(
        db_session,
        course=course,
        user=user,
        subtopic=subtopic,
        multiple_choice=True,
    )

    attempts = await QuestionAttemptRepository(db_session).bulk_create(
        test_progress_id=progress.id,
        attempts=[
            QuestionAttemptDraft(
                question_id=question.id,
                selected_option_ids=[options[0].id, options[1].id],
                is_correct=True,
            )
        ],
    )
    await db_session.flush()

    rows = (
        await db_session.execute(select(QuestionAttemptSelectedOption))
    ).scalars().all()
    assert attempts[0].test_progress_id == progress.id
    assert not hasattr(attempts[0], "selected_option_id")
    assert {row.answer_option_id for row in rows} == {
        options[0].id,
        options[1].id,
    }


@pytest.mark.asyncio
async def test_find_by_test_progress_loads_selected_options(
    db_session,
) -> None:
    user = await create_user(db_session)
    course = await create_course(db_session, creator=user)
    subtopic = await add_course_structure(db_session, course)
    _, question, options, progress = await create_test_with_questions(
        db_session,
        course=course,
        user=user,
        subtopic=subtopic,
        multiple_choice=True,
    )
    repository = QuestionAttemptRepository(db_session)
    await repository.bulk_create(
        test_progress_id=progress.id,
        attempts=[
            QuestionAttemptDraft(
                question_id=question.id,
                selected_option_ids=[options[0].id, options[1].id],
                is_correct=True,
            )
        ],
    )

    attempts = await repository.find_by_test_progress_id(progress.id)

    assert len(attempts) == 1
    assert {
        selected.answer_option_id for selected in attempts[0].selected_options
    } == {options[0].id, options[1].id}
