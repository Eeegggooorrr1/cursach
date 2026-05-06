from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import Question, Test
from models.progress import TestProgress, TestProgressStatusEnum


@dataclass
class TestProgressRepository:
    session: AsyncSession

    async def create_in_progress(
        self,
        user_id: int,
        test_id: int,
    ) -> TestProgress:
        progress = TestProgress(
            user_id=user_id,
            test_id=test_id,
            status=TestProgressStatusEnum.IN_PROGRESS,
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
                Test.user_id == user_id,
            )
            .order_by(TestProgress.started_at.desc())
            .limit(limit)
            .subquery()
        )

        stmt = (
            select(Question.prompt)
            .join(latest_tests, latest_tests.c.test_id == Question.test_id)
            .order_by(
                latest_tests.c.started_at.desc(), Question.position.asc()
            )
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_for_update_by_user_and_test(
        self,
        user_id: int,
        test_id: int,
    ) -> TestProgress | None:
        stmt = (
            select(TestProgress)
            .where(
                TestProgress.user_id == user_id,
                TestProgress.test_id == test_id,
            )
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_finished(
        self,
        progress: TestProgress,
        *,
        correct_percentage: float,
    ) -> TestProgress:
        progress.status = TestProgressStatusEnum.FINISHED
        progress.correct_percentage = correct_percentage
        progress.finished_at = datetime.now(timezone.utc)
        await self.session.flush()
        return progress

    async def get_course_history(
        self,
        user_id: int,
        course_id: int,
        limit: int,
        offset: int,
    ) -> list[tuple[Test, TestProgress]]:
        stmt = (
            select(Test, TestProgress)
            .join(TestProgress, TestProgress.test_id == Test.id)
            .where(
                Test.course_id == course_id,
                Test.user_id == user_id,
                TestProgress.user_id == user_id,
            )
            .order_by(TestProgress.started_at.desc(), TestProgress.id.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.all())

    async def count_course_history(
        self,
        user_id: int,
        course_id: int,
    ) -> int:
        stmt = (
            select(func.count(TestProgress.id))
            .select_from(TestProgress)
            .join(Test, Test.id == TestProgress.test_id)
            .where(
                Test.course_id == course_id,
                Test.user_id == user_id,
                TestProgress.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def find_by_user_and_test(
        self,
        user_id: int,
        test_id: int,
    ) -> TestProgress | None:
        stmt = select(TestProgress).where(
            TestProgress.user_id == user_id,
            TestProgress.test_id == test_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
