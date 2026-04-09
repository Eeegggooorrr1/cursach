from dishka import Provider, provide, Scope

from core.config import Settings


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return Settings()
