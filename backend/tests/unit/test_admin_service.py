from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from core.exceptions import BadRequestError
from services.admin import AdminService


def make_cache() -> SimpleNamespace:
    return SimpleNamespace(
        delete=AsyncMock(),
        delete_pattern=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_admin_restricts_course_public_access() -> None:
    course = SimpleNamespace(
        id=7,
        creator_id=5,
        title="Course",
        comment=None,
        prompt=None,
        is_public=False,
        is_public_allowed=False,
        created_at=datetime.now(timezone.utc),
    )
    course_repository = SimpleNamespace(
        get_course_by_id=AsyncMock(return_value=course),
        set_admin_public_access=AsyncMock(return_value=course),
    )
    service = AdminService(
        user_repository=SimpleNamespace(),
        course_repository=course_repository,
        refresh_repository=SimpleNamespace(),
        cache=make_cache(),
    )

    await service.restrict_course_public_access(admin_id=1, course_id=7)

    course_repository.set_admin_public_access.assert_awaited_once_with(
        course,
        is_public=False,
        is_public_allowed=False,
    )


@pytest.mark.asyncio
async def test_admin_cannot_block_himself() -> None:
    service = AdminService(
        user_repository=SimpleNamespace(),
        course_repository=SimpleNamespace(),
        refresh_repository=SimpleNamespace(),
        cache=make_cache(),
    )

    with pytest.raises(BadRequestError):
        await service.block_user(admin_id=3, user_id=3)


@pytest.mark.asyncio
async def test_blocking_user_revokes_refresh_tokens() -> None:
    user = SimpleNamespace(
        id=5,
        email="blocked@example.com",
        username="blocked",
        profile_description=None,
        is_blocked=True,
        role=SimpleNamespace(name="user"),
    )
    user_repository = SimpleNamespace(
        find_user_by_id=AsyncMock(return_value=user),
        set_blocked=AsyncMock(return_value=user),
    )
    refresh_repository = SimpleNamespace(
        revoke_all_for_user=AsyncMock(),
    )
    service = AdminService(
        user_repository=user_repository,
        course_repository=SimpleNamespace(),
        refresh_repository=refresh_repository,
        cache=make_cache(),
    )

    await service.block_user(admin_id=1, user_id=5)

    user_repository.set_blocked.assert_awaited_once_with(user, True)
    refresh_repository.revoke_all_for_user.assert_awaited_once_with(5)
