from dishka import Provider, provide, Scope
from passlib.context import CryptContext


class CryptProvider(Provider):
    @provide(scope=Scope.APP)
    def pwd_context(self) -> CryptContext:
        return CryptContext(schemes=["bcrypt"], deprecated="auto")
