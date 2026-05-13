from dataclasses import dataclass

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.progress import CourseProgress, CourseProgressStatusEnum


@dataclass
class CourseProgressRepository:
    session: AsyncSession

    async def find_by_course_and_user(
        self,
        course_id: int,
        user_id: int,
    ) -> CourseProgress | None:
        stmt = select(CourseProgress).where(
            CourseProgress.course_id == course_id,
            CourseProgress.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        course_id: int,
        user_id: int,
        status: str = CourseProgressStatusEnum.ACTIVE,
    ) -> CourseProgress:
        progress = CourseProgress(
            course_id=course_id,
            user_id=user_id,
            status=status,
        )
        self.session.add(progress)
        await self.session.flush()
        return progress

    async def mark_completed(
        self,
        course_id: int,
        user_id: int,
    ) -> None:
        stmt = (
            update(CourseProgress)
            .where(
                CourseProgress.course_id == course_id,
                CourseProgress.user_id == user_id,
            )
            .values(
                status=CourseProgressStatusEnum.FINISHED,
                completed_at=func.now(),
            )
        )
        await self.session.execute(stmt)
