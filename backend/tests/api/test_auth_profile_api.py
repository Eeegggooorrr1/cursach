import pytest

from core.auth.tokens import REFRESH_TOKEN_COOKIE
from schemas.validation import (
    AUTH_PASSWORD_MIN_LENGTH,
    PROFILE_DESCRIPTION_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
)


pytestmark = [pytest.mark.api, pytest.mark.integration]


@pytest.mark.asyncio
async def test_register_sets_cookies_and_profile_can_be_updated(
    api_client,
) -> None:
    response = await api_client.post(
        "/auth/register",
        json={
            "email": "profile@example.com",
            "password": "secret123",
            "username": "profile-user",
            "profile_description": "initial description",
        },
    )

    assert response.status_code == 200
    assert "user_access_token" in response.cookies
    assert "user_refresh_token" in response.cookies

    profile = await api_client.get("/profile/")
    assert profile.status_code == 200
    assert profile.json()["email"] == "profile@example.com"
    assert profile.json()["profile_description"] == "initial description"
    assert profile.json()["is_blocked"] is False

    updated = await api_client.patch(
        "/profile/",
        json={"profile_description": "  keep my spacing  "},
    )

    assert updated.status_code == 200
    assert updated.json()["profile_description"] == "  keep my spacing  "


@pytest.mark.asyncio
async def test_login_rejects_invalid_password(api_client) -> None:
    await api_client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "secret123",
            "username": "login-user",
        },
    )

    response = await api_client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_login_or_password"


@pytest.mark.asyncio
async def test_logout_clears_session_cookies_and_profile_becomes_unauthorized(
    api_client,
) -> None:
    register = await api_client.post(
        "/auth/register",
        json={
            "email": "logout@example.com",
            "password": "secret123",
            "username": "logout-user",
        },
    )
    refresh_token = register.cookies.get(REFRESH_TOKEN_COOKIE)
    assert refresh_token is not None

    logout = await api_client.post("/auth/logout")

    assert logout.status_code == 200
    assert "user_access_token" not in api_client.cookies
    assert "user_refresh_token" not in api_client.cookies

    profile = await api_client.get("/profile/")
    assert profile.status_code == 401

    api_client.cookies.set(REFRESH_TOKEN_COOKIE, refresh_token)
    refresh = await api_client.post("/auth/refresh")
    assert refresh.status_code == 401


@pytest.mark.asyncio
async def test_refresh_rotates_refresh_token_and_old_one_is_rejected(
    api_client,
) -> None:
    register = await api_client.post(
        "/auth/register",
        json={
            "email": "refresh@example.com",
            "password": "secret123",
            "username": "refresh-user",
        },
    )
    assert register.status_code == 200
    old_refresh_token = register.cookies.get(REFRESH_TOKEN_COOKIE)
    assert old_refresh_token is not None

    refreshed = await api_client.post("/auth/refresh")

    assert refreshed.status_code == 200
    new_refresh_token = refreshed.cookies.get(REFRESH_TOKEN_COOKIE)
    assert new_refresh_token is not None
    assert new_refresh_token != old_refresh_token

    api_client.cookies.set(REFRESH_TOKEN_COOKIE, old_refresh_token)
    replay = await api_client.post("/auth/refresh")
    assert replay.status_code == 401


@pytest.mark.asyncio
async def test_register_rejects_invalid_user_input(api_client) -> None:
    too_long_username = "u" * (USERNAME_MAX_LENGTH + 1)

    response = await api_client.post(
        "/auth/register",
        json={
            "email": "invalid-register@example.com",
            "password": "x" * AUTH_PASSWORD_MIN_LENGTH,
            "username": too_long_username,
        },
    )
    assert response.status_code == 422

    short_password = await api_client.post(
        "/auth/register",
        json={
            "email": "short-password@example.com",
            "password": "x" * (AUTH_PASSWORD_MIN_LENGTH - 1),
            "username": "valid-user",
        },
    )
    assert short_password.status_code == 422


@pytest.mark.asyncio
async def test_profile_rejects_too_long_description(api_client) -> None:
    await api_client.post(
        "/auth/register",
        json={
            "email": "long-profile@example.com",
            "password": "secret123",
            "username": "long-profile",
        },
    )

    response = await api_client.patch(
        "/profile/",
        json={"profile_description": "x" * (PROFILE_DESCRIPTION_MAX_LENGTH + 1)},
    )

    assert response.status_code == 422
