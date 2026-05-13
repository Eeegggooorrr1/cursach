from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.dto import QuestionAttemptDraft
from models.progress import QuestionAttempt, QuestionAttemptSelectedOption


@dataclass
class QuestionAttemptRepository:
    session: AsyncSession

    async def bulk_create(
        self,
        test_progress_id: int,
        attempts: list[QuestionAttemptDraft],
    ) -> list[QuestionAttempt]:
        rows: list[QuestionAttempt] = []
        for item in attempts:
            selected_option_ids = list(item.selected_option_ids)
            row = QuestionAttempt(
                test_progress_id=test_progress_id,
                question_id=item.question_id,
                is_correct=item.is_correct,
            )
            row.selected_options = [
                QuestionAttemptSelectedOption(answer_option_id=option_id)
                for option_id in selected_option_ids
            ]
            rows.append(row)

        self.session.add_all(rows)
        await self.session.flush()
        return rows

    async def find_by_test_progress_id(
        self,
        test_progress_id: int,
    ) -> list[QuestionAttempt]:
        stmt = (
            select(QuestionAttempt)
            .where(
                QuestionAttempt.test_progress_id == test_progress_id,
            )
            .options(selectinload(QuestionAttempt.selected_options))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
