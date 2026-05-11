import pytest

from tests.conftest import (
    add_course_structure,
    auth_cookies_for_user,
    create_course,
    create_test_with_questions,
    create_user,
    generated_course_response,
    generated_test_response,
    use_auth_cookies,
)


pytestmark = [pytest.mark.api, pytest.mark.integration]


@pytest.mark.asyncio
async def test_create_course_initializes_progress_and_generates_user_test(
    api_client,
    fake_llm_client,
) -> None:
    fake_llm_client.enqueue(
        generated_course_response(
            title="Python",
            topics=["Python"],
            subtopics_count=8,
        )
    )

    await api_client.post(
        "/auth/register",
        json={
            "email": "creator@example.com",
            "password": "secret123",
            "username": "creator",
        },
    )

    created = await api_client.post(
        "/courses/",
        json={
            "title": "Python",
            "comment": "visible comment",
            "prompt": "ask practical questions",
            "topics": ["Python"],
            "initial_difficulty": 2,
            "is_public": True,
        },
    )

    assert created.status_code == 200
    course = created.json()
    course_id = course["id"]
    subtopic_names = [
        subtopic["name"]
        for topic in course["topics"]
        for subtopic in topic["subtopics"]
    ]
    assert len(subtopic_names) == 8

    progress = await api_client.get(f"/courses/{course_id}/progress")
    assert progress.status_code == 200
    assert {item["current_difficulty"] for item in progress.json()["items"]} == {
        2
    }

    fake_llm_client.enqueue(
        generated_test_response(
            topic="Python",
            subtopic_question_counts={
                subtopic_names[0]: 2,
                subtopic_names[1]: 2,
                **{name: 1 for name in subtopic_names[2:]},
            },
        )
    )

    test_response = await api_client.post(f"/courses/{course_id}/create-test")

    assert test_response.status_code == 200
    test_data = test_response.json()
    assert test_data["course_id"] == course_id
    assert len(test_data["questions"]) == 10
    assert any(question["is_multiple_choice"] for question in test_data["questions"])
    assert all(2 <= len(question["options"]) <= 9 for question in test_data["questions"])

    existing_test = await api_client.get(
        f"/courses/{course_id}/tests/{test_data['id']}",
    )
    assert existing_test.status_code == 200
    assert existing_test.json()["id"] == test_data["id"]
    assert len(existing_test.json()["questions"]) == 10


@pytest.mark.asyncio
async def test_public_course_can_be_found_enrolled_and_keeps_private_progress(
    api_client,
    db_session,
    test_settings,
) -> None:
    creator = await create_user(
        db_session,
        email="public-creator@example.com",
        username="public-creator",
    )
    student = await create_user(
        db_session,
        email="public-student@example.com",
        username="public-student",
    )
    course = await create_course(
        db_session,
        creator=creator,
        title="Public SQL",
        is_public=True,
    )
    await add_course_structure(db_session, course)
    await db_session.commit()

    listed = await api_client.get("/courses/public", params={"q": "SQL"})
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()["items"]] == [course.id]

    use_auth_cookies(
        api_client,
        auth_cookies_for_user(student, test_settings),
    )
    enrolled = await api_client.post(
        f"/courses/{course.id}/enroll",
        json={"initial_difficulty": 2},
    )

    assert enrolled.status_code == 200
    assert enrolled.json()["enrolled"] is True

    membership = await api_client.get(
        f"/courses/{course.id}/membership",
    )
    assert membership.status_code == 200
    assert membership.json() == {
        "course_id": course.id,
        "user_id": student.id,
        "enrolled": True,
        "owned": False,
    }

    progress = await api_client.get(
        f"/courses/{course.id}/progress",
    )
    assert progress.status_code == 200
    assert progress.json()["items"][0]["current_difficulty"] == 2


@pytest.mark.asyncio
async def test_course_dashboard_summary_returns_week_stats_and_last_test(
    api_client,
    db_session,
    test_settings,
) -> None:
    user = await create_user(
        db_session,
        email="summary@example.com",
        username="summary-user",
    )
    course = await create_course(
        db_session,
        creator=user,
        title="Summary course",
        is_public=False,
    )
    subtopic = await add_course_structure(db_session, course)
    test, question, options, _ = await create_test_with_questions(
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

    submitted = await api_client.post(
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
    assert submitted.status_code == 200

    summary = await api_client.get("/courses/summary")
    assert summary.status_code == 200
    body = summary.json()
    assert body["active_courses"] == 1
    assert body["tests_last_week"] == 1
    assert body["shared_courses"] == 0
    assert body["public_courses"] == 0
    assert body["last_test"] == {
        "course_id": course.id,
        "test_id": test.id,
        "course_title": "Summary course",
        "test_title": "Test",
        "questions_count": 1,
        "incorrect_answers_count": 0,
        "correct_percentage": 100.0,
        "started_at": body["last_test"]["started_at"],
        "finished_at": body["last_test"]["finished_at"],
    }


@pytest.mark.asyncio
async def test_public_course_detail_is_available_without_auth_and_enroll_requires_auth(
    api_client,
    db_session,
) -> None:
    creator = await create_user(
        db_session,
        email="guest-catalog@example.com",
        username="guest-catalog",
    )
    course = await create_course(
        db_session,
        creator=creator,
        title="Open course",
        is_public=True,
    )
    await add_course_structure(db_session, course)
    await db_session.commit()

    detail = await api_client.get(f"/courses/public/{course.id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == course.id

    enroll = await api_client.post(
        f"/courses/{course.id}/enroll",
        json={"initial_difficulty": 1},
    )
    assert enroll.status_code == 401


@pytest.mark.asyncio
async def test_deleting_unshared_owned_course_removes_it_completely(
    api_client,
    db_session,
    test_settings,
) -> None:
    owner = await create_user(
        db_session,
        email="solo-owner@example.com",
        username="solo-owner",
    )
    course = await create_course(
        db_session,
        creator=owner,
        title="Solo course",
        is_public=True,
    )
    await add_course_structure(db_session, course)
    await db_session.commit()

    use_auth_cookies(api_client, auth_cookies_for_user(owner, test_settings))
    deleted = await api_client.delete(f"/courses/{course.id}")
    assert deleted.status_code == 204

    public_detail = await api_client.get(f"/courses/public/{course.id}")
    assert public_detail.status_code == 404


@pytest.mark.asyncio
async def test_deleting_shared_course_removes_only_requesting_user_data(
    api_client,
    db_session,
    test_settings,
) -> None:
    owner = await create_user(
        db_session,
        email="shared-owner@example.com",
        username="shared-owner",
    )
    student = await create_user(
        db_session,
        email="shared-student@example.com",
        username="shared-student",
    )
    course = await create_course(
        db_session,
        creator=owner,
        title="Shared course",
        is_public=True,
    )
    await add_course_structure(db_session, course)
    await db_session.commit()

    use_auth_cookies(api_client, auth_cookies_for_user(student, test_settings))
    enrolled = await api_client.post(
        f"/courses/{course.id}/enroll",
        json={"initial_difficulty": 2},
    )
    assert enrolled.status_code == 200

    use_auth_cookies(api_client, auth_cookies_for_user(owner, test_settings))
    deleted = await api_client.delete(f"/courses/{course.id}")
    assert deleted.status_code == 204

    owner_detail = await api_client.get(f"/courses/{course.id}")
    assert owner_detail.status_code == 404

    public_detail = await api_client.get(f"/courses/public/{course.id}")
    assert public_detail.status_code == 200
    assert public_detail.json()["id"] == course.id

    use_auth_cookies(api_client, auth_cookies_for_user(student, test_settings))
    student_detail = await api_client.get(f"/courses/{course.id}")
    assert student_detail.status_code == 200
    assert student_detail.json()["course"]["id"] == course.id
