from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.course import CourseRepository
from repositories.course_progress import CourseProgressRepository
from repositories.question_attempt import QuestionAttemptRepository
from repositories.refresh_token import RefreshTokenRepository
from repositories.subtopic import SubtopicRepository
from repositories.subtopic_progress import SubtopicProgressRepository
from repositories.test import TestRepository
from repositories.test_progress import TestProgressRepository
from repositories.user import UserRepository


class RepositoriesProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def user_repository(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def refresh_repository(
        self, session: AsyncSession
    ) -> RefreshTokenRepository:
        return RefreshTokenRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def test_repository(self, session: AsyncSession) -> TestRepository:
        return TestRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def course_repository(self, session: AsyncSession) -> CourseRepository:
        return CourseRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def course_progress_repository(
        self, session: AsyncSession
    ) -> CourseProgressRepository:
        return CourseProgressRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def subtopic_repository(self, session: AsyncSession) -> SubtopicRepository:
        return SubtopicRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def subtopic_progress_repository(
        self, session: AsyncSession
    ) -> SubtopicProgressRepository:
        return SubtopicProgressRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def test_progress_repository(
        self, session: AsyncSession
    ) -> TestProgressRepository:
        return TestProgressRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def question_attempt_repository(
        self, session: AsyncSession
    ) -> QuestionAttemptRepository:
        return QuestionAttemptRepository(session=session)
