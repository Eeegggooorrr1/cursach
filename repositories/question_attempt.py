from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dto import QuestionAttemptDraft
from models.progress import QuestionAttempt


class QuestionAttemptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_create(
        self,
        test_progress_id: int,
        attempts: list[QuestionAttemptDraft],
    ) -> list[QuestionAttempt]:
        rows = [
            QuestionAttempt(
                course_test_progress_id=test_progress_id,
                question_id=item.question_id,
                selected_option_id=item.selected_option_id,
                is_correct=item.is_correct,
            )
            for item in attempts
        ]
        self.session.add_all(rows)
        await self.session.flush()
        return rows

    async def find_by_test_progress_id(
        self,
        test_progress_id: int,
    ) -> list[QuestionAttempt]:
        stmt = select(QuestionAttempt).where(
            QuestionAttempt.course_test_progress_id == test_progress_id,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
