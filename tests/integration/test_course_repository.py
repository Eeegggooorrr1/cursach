import pytest

from models.user import UserCourse
from repositories.course import CourseRepository
from tests.conftest import create_course, create_user


pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_admin_public_access_flags_are_persisted(db_session) -> None:
    user = await create_user(db_session)
    course = await create_course(
        db_session,
        creator=user,
        is_public=True,
        is_public_allowed=True,
    )
    repository = CourseRepository(db_session)

    await repository.set_admin_public_access(
        course,
        is_public=False,
        is_public_allowed=False,
    )

    loaded = await repository.get_course_by_id(course.id)
    assert loaded is not None
    assert loaded.is_public is False
    assert loaded.is_public_allowed is False


@pytest.mark.asyncio
async def test_public_search_ignores_admin_restricted_courses(
    db_session,
) -> None:
    user = await create_user(db_session)
    visible = await create_course(
        db_session,
        creator=user,
        title="Visible",
        is_public=True,
    )
    restricted = await create_course(
        db_session,
        creator=user,
        title="Restricted",
        is_public=False,
        is_public_allowed=False,
    )
    repository = CourseRepository(db_session)

    public_courses = await repository.find_public_courses_paginated(
        limit=20,
        offset=0,
    )
    restricted_courses = await repository.find_restricted_courses_paginated(
        limit=20,
        offset=0,
    )

    assert [course.id for course in public_courses] == [visible.id]
    assert [course.id for course in restricted_courses] == [restricted.id]


@pytest.mark.asyncio
async def test_add_user_course_creates_membership_once(db_session) -> None:
    creator = await create_user(db_session, email="creator@example.com")
    student = await create_user(
        db_session,
        email="student@example.com",
        username="student",
    )
    course = await create_course(db_session, creator=creator, is_public=True)
    repository = CourseRepository(db_session)

    first = await repository.add_user_course(
        user_id=student.id,
        course_id=course.id,
    )
    second = await repository.add_user_course(
        user_id=student.id,
        course_id=course.id,
    )
    link = await repository.find_user_course_link(
        user_id=student.id,
        course_id=course.id,
    )

    assert first is True
    assert second is False
    assert isinstance(link, UserCourse)
