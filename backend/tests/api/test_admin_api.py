import pytest

from tests.conftest import (
    auth_cookies_for_user,
    create_course,
    create_user,
    use_auth_cookies,
)


pytestmark = [pytest.mark.api, pytest.mark.integration]


@pytest.mark.asyncio
async def test_admin_restricts_and_restores_course_public_access(
    api_client,
    db_session,
    test_settings,
) -> None:
    admin = await create_user(
        db_session,
        email="admin@example.com",
        username="admin",
        role_id=2,
    )
    creator = await create_user(
        db_session,
        email="course-owner@example.com",
        username="course-owner",
    )
    course = await create_course(
        db_session,
        creator=creator,
        title="Public course",
        is_public=True,
    )
    await db_session.commit()

    admin_cookies = auth_cookies_for_user(admin, test_settings)
    creator_cookies = auth_cookies_for_user(creator, test_settings)

    use_auth_cookies(api_client, admin_cookies)
    restricted = await api_client.patch(
        f"/admin/courses/{course.id}/restrict-public",
    )

    assert restricted.status_code == 200
    assert restricted.json()["is_public"] is False
    assert restricted.json()["is_public_allowed"] is False

    use_auth_cookies(api_client, creator_cookies)
    republish = await api_client.patch(
        f"/courses/{course.id}/visibility",
        json={"is_public": True},
    )
    assert republish.status_code == 403
    assert republish.json()["error"]["code"] == "course_public_access_restricted"

    use_auth_cookies(api_client, admin_cookies)
    restricted_list = await api_client.get(
        "/admin/restricted-courses",
    )
    assert restricted_list.status_code == 200
    assert [item["id"] for item in restricted_list.json()["items"]] == [
        course.id
    ]

    use_auth_cookies(api_client, admin_cookies)
    restored = await api_client.patch(
        f"/admin/courses/{course.id}/restore-public",
    )
    assert restored.status_code == 200
    assert restored.json()["is_public"] is True
    assert restored.json()["is_public_allowed"] is True


@pytest.mark.asyncio
async def test_admin_blocks_user_and_guard_uses_token_blocked_claim(
    api_client,
    db_session,
    test_settings,
) -> None:
    admin = await create_user(
        db_session,
        email="block-admin@example.com",
        username="block-admin",
        role_id=2,
    )
    user = await create_user(
        db_session,
        email="blocked-by-admin@example.com",
        username="blocked-by-admin",
    )
    await db_session.commit()

    admin_cookies = auth_cookies_for_user(admin, test_settings)
    issued_before_block_cookies = auth_cookies_for_user(user, test_settings)

    use_auth_cookies(api_client, admin_cookies)
    blocked = await api_client.patch(
        f"/admin/users/{user.id}/block",
    )
    assert blocked.status_code == 200
    assert blocked.json()["is_blocked"] is True

    use_auth_cookies(api_client, issued_before_block_cookies)
    allowed_with_existing_access = await api_client.get("/profile/")
    assert allowed_with_existing_access.status_code == 200

    user.is_blocked = True
    blocked_claim_cookies = auth_cookies_for_user(user, test_settings)
    use_auth_cookies(api_client, blocked_claim_cookies)
    denied = await api_client.get("/profile/")
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "user_blocked"

    use_auth_cookies(api_client, admin_cookies)
    blocked_users = await api_client.get(
        "/admin/blocked-users",
    )
    assert blocked_users.status_code == 200
    assert [item["id"] for item in blocked_users.json()["items"]] == [user.id]

    use_auth_cookies(api_client, admin_cookies)
    unblocked = await api_client.patch(
        f"/admin/users/{user.id}/unblock",
    )
    assert unblocked.status_code == 200
    assert unblocked.json()["is_blocked"] is False

    user.is_blocked = False
    unblocked_claim_cookies = auth_cookies_for_user(user, test_settings)
    use_auth_cookies(api_client, unblocked_claim_cookies)
    allowed = await api_client.get("/profile/")
    assert allowed.status_code == 200
