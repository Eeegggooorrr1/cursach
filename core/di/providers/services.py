from dishka import Provider, provide, Scope
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from ai.contracts import LLMClient
from ai.prompts.test_generation.factory import TestGenerationPromptFactory
from cli.bootstrap.seed_service import SeedService
from core.config import Settings
from repositories.refresh_token import RefreshTokenRepository
from repositories.test import TestRepository
from repositories.user import UserRepository
from services.auth import AuthService
from services.cookie import CookieManager
from services.security import SecurityService
from services.test import TestService


class ServicesProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def security_service(
        self,
        user_repository: UserRepository,
        refresh_repository: RefreshTokenRepository,
        settings: Settings,
        pwd_context: CryptContext,
    ) -> SecurityService:
        return SecurityService(
            user_repository=user_repository,
            refresh_repository=refresh_repository,
            settings=settings,
            pwd_context=pwd_context,
        )

    @provide(scope=Scope.REQUEST)
    def auth_service(
        self,
        user_repository: UserRepository,
        security_service: SecurityService,
    ) -> AuthService:
        return AuthService(
            user_repository=user_repository,
            security_service=security_service,
        )

    @provide(scope=Scope.REQUEST)
    def seed_service(self, session: AsyncSession, settings: Settings) -> SeedService:
        return SeedService(session=session, settings=settings)

    @provide(scope=Scope.REQUEST)
    def cookie_manager(self) -> CookieManager:
        return CookieManager()

    @provide(scope=Scope.REQUEST)
    def test_service(
        self,
        test_repository: TestRepository,
        llm_client: LLMClient,
        test_prompt_factory: TestGenerationPromptFactory,
    ) -> TestService:
        return TestService(
            test_repository=test_repository,
            llm_client=llm_client,
            prompt_factory=test_prompt_factory,
        )
