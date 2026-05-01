from dishka import Provider, provide, Scope
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from ai.contracts import LLMClient
from ai.factories.course_generation_factory import (
    CourseGenerationPromptFactory,
)
from ai.factories.test_generation_factory import \
    TestGenerationPromptFactory
from cli.bootstrap.seed_service import SeedService
from core.config import Settings
from repositories.course import CourseRepository
from repositories.course_progress import CourseProgressRepository
from repositories.question_attempt import QuestionAttemptRepository
from repositories.refresh_token import RefreshTokenRepository
from repositories.subtopic import SubtopicRepository
from repositories.subtopic_progress import SubtopicProgressRepository
from repositories.test import TestRepository
from repositories.test_progress import TestProgressRepository
from repositories.user import UserRepository
from services.auth import AuthService
from services.cookie import CookieManager
from services.course import CourseService, CourseGenerationPolicy
from services.security import SecurityService
from services.submission import TestSubmissionPolicy, \
    TestSubmissionService
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
    def seed_service(
        self, session: AsyncSession, settings: Settings
    ) -> SeedService:
        return SeedService(session=session, settings=settings)

    @provide(scope=Scope.REQUEST)
    def cookie_manager(self) -> CookieManager:
        return CookieManager()

    @provide(scope=Scope.REQUEST)
    def test_service(
        self,
        course_repository: CourseRepository,
        course_progress_repository: CourseProgressRepository,
        subtopic_progress_repository: SubtopicProgressRepository,
        test_progress_repository: TestProgressRepository,
        subtopic_repository: SubtopicRepository,
        test_repository: TestRepository,
        question_attempt_repository: QuestionAttemptRepository,
        llm_client: LLMClient,
        prompt_factory: TestGenerationPromptFactory,
    ) -> TestService:
        return TestService(
            course_repository=course_repository,
            course_progress_repository=course_progress_repository,
            subtopic_progress_repository=subtopic_progress_repository,
            test_progress_repository=test_progress_repository,
            subtopic_repository=subtopic_repository,
            test_repository=test_repository,
            question_attempt_repository=question_attempt_repository,
            llm_client=llm_client,
            prompt_factory=prompt_factory,
        )

    @provide(scope=Scope.REQUEST)
    def course_service(
        self,
        course_repository: CourseRepository,
        course_progress_repository: CourseProgressRepository,
        llm_client: LLMClient,
        course_prompt_factory: CourseGenerationPromptFactory,
        course_policy: CourseGenerationPolicy,
        test_progress_repository: TestProgressRepository,
        subtopic_repository: SubtopicRepository,
        subtopic_progress_repository: SubtopicProgressRepository,
    ) -> CourseService:
        return CourseService(
            course_repository=course_repository,
            course_progress_repository=course_progress_repository,
            llm_client=llm_client,
            prompt_factory=course_prompt_factory,
            course_policy=course_policy,
            test_progress_repository=test_progress_repository,
            subtopic_repository=subtopic_repository,
            subtopic_progress_repository=subtopic_progress_repository,
        )

    @provide(scope=Scope.REQUEST)
    def submission_service(
        self,
        course_progress_repository: CourseProgressRepository,
        test_repository: TestRepository,
        test_progress_repository: TestProgressRepository,
        question_attempt_repository: QuestionAttemptRepository,
        subtopic_progress_repository: SubtopicProgressRepository,
        submission_policy: TestSubmissionPolicy,
    ) -> TestSubmissionService:
        return TestSubmissionService(
            course_progress_repository=course_progress_repository,
            test_repository=test_repository,
            test_progress_repository=test_progress_repository,
            question_attempt_repository=question_attempt_repository,
            subtopic_progress_repository=subtopic_progress_repository,
            submission_policy=submission_policy,
        )

    @provide(scope=Scope.REQUEST)
    def submission_policy(self) -> TestSubmissionPolicy:
        return TestSubmissionPolicy()

    @provide(scope=Scope.REQUEST)
    def course_policy(self) -> CourseGenerationPolicy:
        return CourseGenerationPolicy()
