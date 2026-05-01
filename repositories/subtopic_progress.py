from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dto import SubtopicProgressUpdate
from models.progress import SubtopicProgress


class SubtopicProgressRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_user_and_subtopic_ids(
        self,
        user_id: int,
        subtopic_ids: list[int],
    ) -> list[SubtopicProgress]:
        if not subtopic_ids:
            return []

        stmt = select(SubtopicProgress).where(
            SubtopicProgress.user_id == user_id,
            SubtopicProgress.subtopic_id.in_(subtopic_ids),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert_many(
        self,
        *,
        user_id: int,
        updates: list[SubtopicProgressUpdate],
    ) -> list[SubtopicProgress]:
        if not updates:
            return []

        subtopic_ids = [item.subtopic_id for item in updates]
        existing = await self.find_by_user_and_subtopic_ids(
            user_id=user_id,
            subtopic_ids=subtopic_ids,
        )
        existing_by_id = {item.subtopic_id: item for item in existing}

        result: list[SubtopicProgress] = []

        for item in updates:
            progress = existing_by_id.get(item.subtopic_id)
            if progress is None:
                progress = SubtopicProgress(
                    user_id=user_id,
                    subtopic_id=item.subtopic_id,
                    mastery_score=item.mastery_score,
                    current_difficulty=item.current_difficulty,
                    current_streak=item.current_streak,
                )
                self.session.add(progress)
            else:
                progress.mastery_score = item.mastery_score
                progress.current_difficulty = item.current_difficulty
                progress.current_streak = item.current_streak

            result.append(progress)

        await self.session.flush()
        return result
