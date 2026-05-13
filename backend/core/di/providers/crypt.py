from dishka import Provider, provide, Scope
from passlib.context import CryptContext

from core.crypt import create_password_context


class CryptProvider(Provider):
    @provide(scope=Scope.APP)
    def pwd_context(self) -> CryptContext:
        return create_password_context()
