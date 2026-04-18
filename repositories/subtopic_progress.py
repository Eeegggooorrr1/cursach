from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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