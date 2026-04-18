from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Subtopic, Topic


class SubtopicRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_course_id(self, course_id: int) -> list[Subtopic]:
        stmt = (
            select(Subtopic)
            .join(Topic, Topic.id == Subtopic.topic_id)
            .where(Topic.course_id == course_id)
            .order_by(Topic.id, Subtopic.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())