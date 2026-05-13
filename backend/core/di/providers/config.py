from dishka import Provider, provide, Scope

from core.config import Settings, create_settings


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return create_settings()
