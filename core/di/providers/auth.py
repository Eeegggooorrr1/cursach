from dishka import Provider, provide, Scope
from starlette.requests import Request

from core.auth.current_user import get_current_user_from_token
from core.auth.tokens import (
    AccessToken,
    RefreshToken,
    get_access_token,
    get_refresh_token,
)
from schemas.auth import UserFromToken
from services.security import SecurityService


class AuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def access_token(self, request: Request) -> AccessToken:
        return get_access_token(request)

    @provide(scope=Scope.REQUEST)
    def refresh_token(self, request: Request) -> RefreshToken:
        return get_refresh_token(request)

    @provide(scope=Scope.REQUEST)
    def current_user(
        self,
        access_token: AccessToken,
        security_service: SecurityService,
    ) -> UserFromToken:
        return get_current_user_from_token(
            access_token=access_token,
            security_service=security_service,
        )
