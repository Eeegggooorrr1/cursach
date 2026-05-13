from core.auth.tokens import AccessToken
from schemas.auth import UserFromToken
from services.security import SecurityService


def get_current_user_from_token(
    access_token: AccessToken,
    security_service: SecurityService,
) -> UserFromToken:
    payload = security_service.decode_token(
        access_token,
        expected_name="access",
    )

    return UserFromToken(
        id=int(payload["sub"]),
        username=payload["username"],
        role=payload["role"],
        is_blocked=bool(payload.get("is_blocked", False)),
    )
