from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models import Question, Test
from models.progress import TestProgress


class TestProgressRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_in_progress(
        self,
        user_id: int,
        test_id: int,
    ) -> TestProgress:
        progress = TestProgress(
            user_id=user_id,
            test_id=test_id,
            status="in_progress",
        )
        self.session.add(progress)
        await self.session.flush()
        return progress

    async def get_last_questions(
        self,
        course_id: int,
        user_id: int,
        limit: int = 3,
    ) -> list[str]:
        latest_tests = (
            select(
                TestProgress.test_id.label("test_id"),
                TestProgress.started_at.label("started_at"),
            )
            .join(Test, Test.id == TestProgress.test_id)
            .where(
                TestProgress.user_id == user_id,
                Test.course_id == course_id,
            )
            .order_by(TestProgress.started_at.desc())
            .limit(limit)
            .subquery()
        )

        stmt = (
            select(Question.prompt)
            .join(latest_tests, latest_tests.c.test_id == Question.test_id)
            .order_by(latest_tests.c.started_at.desc(), Question.position.asc())
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())