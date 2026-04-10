from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.course import CourseRepository
from repositories.refresh_token import RefreshTokenRepository
from repositories.test import TestRepository
from repositories.user import UserRepository


class RepositoriesProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def user_repository(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def refresh_repository(self, session: AsyncSession) -> RefreshTokenRepository:
        return RefreshTokenRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def test_repository(self, session: AsyncSession) -> TestRepository:
        return TestRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def course_repository(self, session: AsyncSession) -> CourseRepository:
        return CourseRepository(session=session)