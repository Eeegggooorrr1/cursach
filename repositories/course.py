from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ai.contracts import GeneratedCourseStructureSchema
from models.course import Course, Topic, Subtopic

class CourseRepository:
    model = Course

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_course(
        self,
        user_id: int,
        title: str,
        comment: str | None,
    ) -> Course:
        course = Course(
            user_id=user_id,
            title=title,
            comment=comment,
        )
        self.session.add(course)
        await self.session.flush()
        return course

    async def save_generated_course(
        self,
        course_id: int,
        generated: GeneratedCourseStructureSchema,
    ) -> Course:
        course = await self.get_course_with_details(course_id)

        if not course:
            raise ValueError("Course not found")

        course.topics.clear()

        for topic_position, topic_data in enumerate(generated.topics):
            topic = Topic(
                course_id=course.id,
                name=topic_data.name.strip(),
            )

            for subtopic_position, subtopic_data in enumerate(topic_data.subtopics):
                topic.subtopics.append(
                    Subtopic(
                        name=subtopic_data.name.strip(),
                    )
                )

            course.topics.append(topic)

        await self.session.flush()
        return course

    async def get_course_with_details(self, course_id: int) -> Course | None:
        stmt = (
            select(Course)
            .where(Course.id == course_id)
            .options(
                selectinload(Course.topics).selectinload(Topic.subtopics),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_course_by_id(self, course_id: int) -> Course | None:
        stmt = select(Course).where(Course.id == course_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()