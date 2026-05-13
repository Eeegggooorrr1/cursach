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
from core.cache import CacheService
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
from services.admin import AdminService
from services.auth import AuthService
from services.cookie import CookieManager
from services.course import (
    CourseCacheInvalidationService,
    CourseCreationService,
    CourseDeletionService,
    CourseDetailService,
    CourseGenerationPolicy,
    CourseLearningStateService,
    CourseListService,
    CoursePublicService,
    CourseSearchService,
    CourseService,
)
from services.security import SecurityService
from services.test import (
    TestGenerationService,
    TestQuestionCountPolicy,
    TestReadService,
    TestReviewService,
    TestService,
    TestSubmissionPolicy,
    TestSubmissionService,
)
from services.user import UserService


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
    def user_service(
        self,
        user_repository: UserRepository,
    ) -> UserService:
        return UserService(user_repository=user_repository)

    @provide(scope=Scope.REQUEST)
    def admin_service(
        self,
        user_repository: UserRepository,
        course_repository: CourseRepository,
        refresh_repository: RefreshTokenRepository,
        cache_service: CacheService,
    ) -> AdminService:
        return AdminService(
            user_repository=user_repository,
            course_repository=course_repository,
            refresh_repository=refresh_repository,
            cache=cache_service,
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
    def test_generation_service(
        self,
        course_repository: CourseRepository,
        course_progress_repository: CourseProgressRepository,
        subtopic_progress_repository: SubtopicProgressRepository,
        test_progress_repository: TestProgressRepository,
        subtopic_repository: SubtopicRepository,
        test_repository: TestRepository,
        llm_client: LLMClient,
        prompt_factory: TestGenerationPromptFactory,
        question_count_policy: TestQuestionCountPolicy,
        cache_service: CacheService,
    ) -> TestGenerationService:
        return TestGenerationService(
            course_repository=course_repository,
            course_progress_repository=course_progress_repository,
            subtopic_progress_repository=subtopic_progress_repository,
            test_progress_repository=test_progress_repository,
            subtopic_repository=subtopic_repository,
            test_repository=test_repository,
            llm_client=llm_client,
            prompt_factory=prompt_factory,
            question_count_policy=question_count_policy,
            cache=cache_service,
        )

    @provide(scope=Scope.REQUEST)
    def test_read_service(
        self,
        test_repository: TestRepository,
        cache_service: CacheService,
    ) -> TestReadService:
        return TestReadService(
            test_repository=test_repository,
            cache=cache_service,
        )

    @provide(scope=Scope.REQUEST)
    def test_review_service(
        self,
        test_repository: TestRepository,
        test_progress_repository: TestProgressRepository,
        question_attempt_repository: QuestionAttemptRepository,
        cache_service: CacheService,
    ) -> TestReviewService:
        return TestReviewService(
            test_repository=test_repository,
            test_progress_repository=test_progress_repository,
            question_attempt_repository=question_attempt_repository,
            cache=cache_service,
        )

    @provide(scope=Scope.REQUEST)
    def test_service(
        self,
        generation_service: TestGenerationService,
        read_service: TestReadService,
        review_service: TestReviewService,
    ) -> TestService:
        return TestService(
            generation_service=generation_service,
            read_service=read_service,
            review_service=review_service,
        )

    @provide(scope=Scope.REQUEST)
    def course_cache_invalidation_service(
        self,
        cache_service: CacheService,
    ) -> CourseCacheInvalidationService:
        return CourseCacheInvalidationService(cache=cache_service)

    @provide(scope=Scope.REQUEST)
    def course_learning_state_service(
        self,
        course_progress_repository: CourseProgressRepository,
        subtopic_repository: SubtopicRepository,
        subtopic_progress_repository: SubtopicProgressRepository,
    ) -> CourseLearningStateService:
        return CourseLearningStateService(
            course_progress_repository=course_progress_repository,
            subtopic_repository=subtopic_repository,
            subtopic_progress_repository=subtopic_progress_repository,
        )

    @provide(scope=Scope.REQUEST)
    def course_creation_service(
        self,
        course_repository: CourseRepository,
        llm_client: LLMClient,
        course_prompt_factory: CourseGenerationPromptFactory,
        course_policy: CourseGenerationPolicy,
        course_learning_state_service: CourseLearningStateService,
        course_cache_invalidation_service: CourseCacheInvalidationService,
    ) -> CourseCreationService:
        return CourseCreationService(
            course_repository=course_repository,
            llm_client=llm_client,
            prompt_factory=course_prompt_factory,
            course_policy=course_policy,
            learning_state_service=course_learning_state_service,
            cache_invalidation_service=course_cache_invalidation_service,
        )

    @provide(scope=Scope.REQUEST)
    def course_list_service(
        self,
        course_repository: CourseRepository,
        test_progress_repository: TestProgressRepository,
    ) -> CourseListService:
        return CourseListService(
            course_repository=course_repository,
            test_progress_repository=test_progress_repository,
        )

    @provide(scope=Scope.REQUEST)
    def course_deletion_service(
        self,
        course_repository: CourseRepository,
        course_cache_invalidation_service: CourseCacheInvalidationService,
    ) -> CourseDeletionService:
        return CourseDeletionService(
            course_repository=course_repository,
            cache_invalidation_service=course_cache_invalidation_service,
        )

    @provide(scope=Scope.REQUEST)
    def course_public_service(
        self,
        course_repository: CourseRepository,
        course_learning_state_service: CourseLearningStateService,
        course_cache_invalidation_service: CourseCacheInvalidationService,
        cache_service: CacheService,
    ) -> CoursePublicService:
        return CoursePublicService(
            course_repository=course_repository,
            learning_state_service=course_learning_state_service,
            cache_invalidation_service=course_cache_invalidation_service,
            cache=cache_service,
        )

    @provide(scope=Scope.REQUEST)
    def course_detail_service(
        self,
        course_repository: CourseRepository,
        test_progress_repository: TestProgressRepository,
        subtopic_repository: SubtopicRepository,
        subtopic_progress_repository: SubtopicProgressRepository,
    ) -> CourseDetailService:
        return CourseDetailService(
            course_repository=course_repository,
            test_progress_repository=test_progress_repository,
            subtopic_repository=subtopic_repository,
            subtopic_progress_repository=subtopic_progress_repository,
        )

    @provide(scope=Scope.REQUEST)
    def course_service(
        self,
        creation_service: CourseCreationService,
        list_service: CourseListService,
        deletion_service: CourseDeletionService,
        public_service: CoursePublicService,
        detail_service: CourseDetailService,
    ) -> CourseService:
        return CourseService(
            creation_service=creation_service,
            list_service=list_service,
            deletion_service=deletion_service,
            public_service=public_service,
            detail_service=detail_service,
        )

    @provide(scope=Scope.REQUEST)
    def course_search_service(
        self,
        course_repository: CourseRepository,
        cache_service: CacheService,
    ) -> CourseSearchService:
        return CourseSearchService(
            course_repository=course_repository,
            cache=cache_service,
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

    @provide(scope=Scope.REQUEST)
    def test_question_count_policy(self) -> TestQuestionCountPolicy:
        return TestQuestionCountPolicy()
