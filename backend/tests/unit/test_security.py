from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from core.exceptions import TokenNotFoundError, UserBlockedError
from models.user import Role, RoleEnum, User
from services.security import SecurityService


@dataclass
class DummySettings:
    SECRET_KEY: str = "test-secret"
    ALGORITHM: str = "HS256"
    ACCESS_EXPIRES_MINUTES: int = 10
    REFRESH_EXPIRES_DAYS: int = 30


class DummyRefreshRepository:
    async def create_and_revoke_all_for_user(self, **kwargs):
        return None


def make_user(*, is_blocked: bool = False) -> User:
    return User(
        id=10,
        email="user@example.com",
        username="user",
        password="hash",
        role=Role(id=1, name=RoleEnum.USER.value),
        is_blocked=is_blocked,
    )


def make_security_service() -> SecurityService:
    return SecurityService(
        user_repository=object(),
        refresh_repository=DummyRefreshRepository(),
        settings=DummySettings(),
        pwd_context=object(),
    )


def test_access_token_contains_blocked_flag() -> None:
    service = make_security_service()

    token = service.issue_access_token(make_user(is_blocked=True))
    payload = service.decode_token(token, expected_name="access")

    assert payload["is_blocked"] is True


@pytest.mark.asyncio
async def test_blocked_user_cannot_receive_token_pair() -> None:
    service = make_security_service()

    with pytest.raises(UserBlockedError):
        await service.issue_token_pair(make_user(is_blocked=True))


@pytest.mark.asyncio
async def test_refresh_revokes_tokens_when_blocked_user_tries_to_refresh() -> None:
    refresh_repository = SimpleNamespace(
        get_by_token=AsyncMock(
            return_value=SimpleNamespace(
                user_id=10,
                revoked_at=None,
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            )
        ),
        revoke_all_for_user=AsyncMock(),
    )
    user_repository = SimpleNamespace(
        find_user_by_id=AsyncMock(return_value=make_user(is_blocked=True))
    )
    service = SecurityService(
        user_repository=user_repository,
        refresh_repository=refresh_repository,
        settings=DummySettings(),
        pwd_context=object(),
    )

    with pytest.raises(UserBlockedError):
        await service.refresh_tokens("refresh-token")

    refresh_repository.revoke_all_for_user.assert_awaited_once_with(10)


@pytest.mark.asyncio
async def test_refresh_raises_not_found_for_unknown_token() -> None:
    refresh_repository = SimpleNamespace(
        get_by_token=AsyncMock(return_value=None),
    )
    service = SecurityService(
        user_repository=SimpleNamespace(),
        refresh_repository=refresh_repository,
        settings=DummySettings(),
        pwd_context=object(),
    )

    with pytest.raises(TokenNotFoundError):
        await service.refresh_tokens("missing-token")
