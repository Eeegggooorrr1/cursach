import pytest

from repositories.user import UserRepository
from tests.conftest import create_user


pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_blocked_users_listing(db_session) -> None:
    blocked = await create_user(
        db_session,
        email="blocked@example.com",
        username="blocked",
        is_blocked=True,
    )
    await create_user(
        db_session,
        email="active@example.com",
        username="active",
        is_blocked=False,
    )
    repository = UserRepository(db_session)

    users = await repository.find_blocked_users_paginated(
        limit=20,
        offset=0,
    )
    total = await repository.count_blocked_users()

    assert total == 1
    assert [user.id for user in users] == [blocked.id]


@pytest.mark.asyncio
async def test_set_blocked_updates_user_flag(db_session) -> None:
    user = await create_user(db_session)
    repository = UserRepository(db_session)

    await repository.set_blocked(user, True)
    loaded = await repository.find_user_by_id(user.id)

    assert loaded is not None
    assert loaded.is_blocked is True
