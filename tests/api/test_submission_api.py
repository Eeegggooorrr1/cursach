import pytest

from tests.conftest import (
    add_course_structure,
    auth_cookies_for_user,
    create_course,
    create_subtopic_progress,
    create_test_with_questions,
    create_user,
    use_auth_cookies,
)


pytestmark = [pytest.mark.api, pytest.mark.integration]


@pytest.mark.asyncio
async def test_submit_multiple_choice_requires_exact_set_and_review_shows_choices(
    api_client,
    db_session,
    test_settings,
) -> None:
    user = await create_user(db_session, email="submitter@example.com")
    course = await create_course(db_session, creator=user)
    subtopic = await add_course_structure(db_session, course)
    test, question, options, _ = await create_test_with_questions(
        db_session,
        course=course,
        user=user,
        subtopic=subtopic,
        multiple_choice=True,
    )
    await create_subtopic_progress(
        db_session,
        user=user,
        subtopic=subtopic,
        mastery_score=0.5,
        current_difficulty=2,
    )
    await db_session.commit()

    use_auth_cookies(
        api_client,
        auth_cookies_for_user(user, test_settings),
    )
    response = await api_client.post(
        f"/courses/{course.id}/{test.id}/submit",
        json={
            "answers": [
                {
                    "question_id": question.id,
                    "selected_option_ids": [options[0].id],
                }
            ]
        },
    )

    assert response.status_code == 200
    assert response.json()["correct_percentage"] == 0.0

    review = await api_client.get(
        f"/courses/{course.id}/{test.id}/review",
    )
    assert review.status_code == 200
    assert review.json()["attempts"] == [
        {
            "question_id": question.id,
            "selected_option_ids": [options[0].id],
            "is_correct": False,
        }
    ]


@pytest.mark.asyncio
async def test_submit_rejects_multiple_selected_options_for_single_choice(
    api_client,
    db_session,
    test_settings,
) -> None:
    user = await create_user(
        db_session,
        email="single-choice@example.com",
        username="single-choice",
    )
    course = await create_course(db_session, creator=user)
    subtopic = await add_course_structure(db_session, course)
    test, question, options, _ = await create_test_with_questions(
        db_session,
        course=course,
        user=user,
        subtopic=subtopic,
        multiple_choice=False,
    )
    await db_session.commit()

    use_auth_cookies(
        api_client,
        auth_cookies_for_user(user, test_settings),
    )
    response = await api_client.post(
        f"/courses/{course.id}/{test.id}/submit",
        json={
            "answers": [
                {
                    "question_id": question.id,
                    "selected_option_ids": [options[0].id, options[1].id],
                }
            ]
        },
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_test_submission"


@pytest.mark.asyncio
async def test_review_is_not_available_while_test_is_in_progress_and_test_can_be_reopened(
    api_client,
    db_session,
    test_settings,
) -> None:
    user = await create_user(
        db_session,
        email="in-progress@example.com",
        username="in-progress",
    )
    course = await create_course(db_session, creator=user)
    subtopic = await add_course_structure(db_session, course)
    test, question, _, _ = await create_test_with_questions(
        db_session,
        course=course,
        user=user,
        subtopic=subtopic,
        multiple_choice=True,
    )
    await db_session.commit()

    use_auth_cookies(
        api_client,
        auth_cookies_for_user(user, test_settings),
    )

    review = await api_client.get(f"/courses/{course.id}/{test.id}/review")
    assert review.status_code == 409
    assert review.json()["error"]["code"] == "test_review_not_available"

    reopened = await api_client.get(f"/courses/{course.id}/tests/{test.id}")
    assert reopened.status_code == 200
    assert reopened.json()["id"] == test.id
    assert reopened.json()["questions"][0]["id"] == question.id
