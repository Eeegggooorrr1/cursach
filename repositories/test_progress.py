from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.course import Course
from models.progress import QuestionAttempt
from models import Question, Test
from models.progress import TestProgress, TestProgressStatusEnum


@dataclass(frozen=True)
class LastFinishedTestSummaryRow:
    course_id: int
    test_id: int
    course_title: str
    test_title: str
    questions_count: int
    correct_answers_count: int
    correct_percentage: float
    started_at: datetime
    finished_at: datetime | None


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

    async def count_started_since(
        self,
        user_id: int,
        since: datetime,
    ) -> int:
        stmt = select(func.count(TestProgress.id)).where(
            TestProgress.user_id == user_id,
            TestProgress.started_at >= since,
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def get_last_finished_summary(
        self,
        user_id: int,
    ) -> LastFinishedTestSummaryRow | None:
        latest_finished_progress_id = (
            select(TestProgress.id)
            .join(Test, Test.id == TestProgress.test_id)
            .where(
                TestProgress.user_id == user_id,
                Test.user_id == user_id,
                TestProgress.status == TestProgressStatusEnum.FINISHED,
            )
            .order_by(TestProgress.finished_at.desc(), TestProgress.id.desc())
            .limit(1)
            .scalar_subquery()
        )

        questions_count = (
            select(func.count(Question.id))
            .where(Question.test_id == Test.id)
            .scalar_subquery()
        )
        correct_answers_count = (
            select(func.count(QuestionAttempt.id))
            .where(
                QuestionAttempt.test_progress_id == TestProgress.id,
                QuestionAttempt.is_correct.is_(True),
            )
            .scalar_subquery()
        )

        stmt = (
            select(
                Test.course_id,
                Test.id,
                Course.title,
                Test.title,
                questions_count,
                correct_answers_count,
                TestProgress.correct_percentage,
                TestProgress.started_at,
                TestProgress.finished_at,
            )
            .join(Test, Test.id == TestProgress.test_id)
            .join(Course, Course.id == Test.course_id)
            .where(TestProgress.id == latest_finished_progress_id)
        )
        row = (await self.session.execute(stmt)).one_or_none()
        if row is None:
            return None

        return LastFinishedTestSummaryRow(
            course_id=row[0],
            test_id=row[1],
            course_title=row[2],
            test_title=row[3],
            questions_count=int(row[4] or 0),
            correct_answers_count=int(row[5] or 0),
            correct_percentage=float(row[6]),
            started_at=row[7],
            finished_at=row[8],
        )
