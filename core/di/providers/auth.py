from dishka import Provider, provide, Scope, FromDishka
from dishka.integrations.fastapi import inject
from fastapi import HTTPException
from starlette import status
from starlette.requests import Request

from core.exceptions import ForbiddenError
from models.user import RoleEnum
from schemas.auth import UserFromToken
from services.security import SecurityService


class AccessToken(str):
    pass


class RefreshToken(str):
    pass


class AuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def access_token(self, request: Request) -> AccessToken:
        token = request.cookies.get("user_access_token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token not found",
            )
        return AccessToken(token)

    @provide(scope=Scope.REQUEST)
    def refresh_token(self, request: Request) -> RefreshToken:
        token = request.cookies.get("user_refresh_token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found",
            )
        return RefreshToken(token)

    @provide(scope=Scope.REQUEST)
    def current_user(
        self,
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
        )


class RequireRoles:
    def __init__(self, *allowed_roles: RoleEnum):
        self.allowed: set[RoleEnum] = set(allowed_roles)

    @inject
    async def __call__(
        self,
        user: FromDishka[UserFromToken],
    ) -> UserFromToken:
        if user.role not in self.allowed:
            raise ForbiddenError(
                message="Insufficient role",
                extra={
                    "required_roles": list(self.allowed),
                    "user_role": user.role,
                },
            )
        return user
