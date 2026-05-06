from dataclasses import dataclass

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ai.schemas import GeneratedCourseStructureSchema
from models.course import Course, Subtopic, Topic
from models.progress import CourseProgress, SubtopicProgress
from models.test import Test
from models.user import UserCourse


@dataclass
class CourseRepository:
    session: AsyncSession

    async def create_course(
        self,
        creator_id: int,
        title: str,
        comment: str | None,
        prompt: str | None,
        is_public: bool,
    ) -> Course:
        course = Course(
            creator_id=creator_id,
            title=title,
            comment=comment,
            prompt=prompt,
            is_public=is_public,
        )
        self.session.add(course)
        await self.session.flush()

        self.session.add(
            UserCourse(user_id=creator_id, course_id=course.id)
        )
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

        for topic_data in generated.topics:
            topic = Topic(
                course_id=course.id,
                name=topic_data.name.strip(),
            )

            for subtopic_data in topic_data.subtopics:
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

    async def find_user_courses_paginated(
        self,
        user_id: int,
        limit: int,
        offset: int,
    ) -> list[Course]:
        stmt = (
            select(Course)
            .join(UserCourse, UserCourse.course_id == Course.id)
            .where(UserCourse.user_id == user_id)
            .order_by(Course.created_at.desc(), Course.id.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_user_courses(self, user_id: int) -> int:
        stmt = (
            select(func.count(Course.id))
            .join(UserCourse, UserCourse.course_id == Course.id)
            .where(UserCourse.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def find_public_courses_paginated(
        self,
        limit: int,
        offset: int,
        query: str | None = None,
        sort: str = "created_desc",
    ) -> list[Course]:
        stmt = (
            select(Course)
            .where(Course.is_public.is_(True))
            .limit(limit)
            .offset(offset)
        )
        if query:
            pattern = f"%{query}%"
            stmt = stmt.where(
                or_(
                    Course.title.ilike(pattern),
                    Course.comment.ilike(pattern),
                )
            )

        if sort == "created_asc":
            stmt = stmt.order_by(Course.created_at.asc(), Course.id.asc())
        else:
            stmt = stmt.order_by(Course.created_at.desc(), Course.id.desc())

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_public_courses(self, query: str | None = None) -> int:
        stmt = select(func.count(Course.id)).where(
            Course.is_public.is_(True)
        )
        if query:
            pattern = f"%{query}%"
            stmt = stmt.where(
                or_(
                    Course.title.ilike(pattern),
                    Course.comment.ilike(pattern),
                )
            )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def find_public_with_details(
        self,
        course_id: int,
    ) -> Course | None:
        stmt = (
            select(Course)
            .where(Course.id == course_id, Course.is_public.is_(True))
            .options(
                selectinload(Course.topics).selectinload(Topic.subtopics),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_and_user(
        self,
        course_id: int,
        user_id: int,
    ) -> Course | None:
        stmt = (
            select(Course)
            .join(UserCourse, UserCourse.course_id == Course.id)
            .where(
                Course.id == course_id,
                UserCourse.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_owned_by_id(
        self,
        course_id: int,
        creator_id: int,
    ) -> Course | None:
        stmt = select(Course).where(
            Course.id == course_id,
            Course.creator_id == creator_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def set_visibility(
        self,
        course: Course,
        is_public: bool,
    ) -> Course:
        course.is_public = is_public
        await self.session.flush()
        return course

    async def find_user_course_link(
        self,
        user_id: int,
        course_id: int,
    ) -> UserCourse | None:
        stmt = select(UserCourse).where(
            UserCourse.user_id == user_id,
            UserCourse.course_id == course_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_user_course(
        self,
        user_id: int,
        course_id: int,
    ) -> bool:
        existing = await self.find_user_course_link(
            user_id=user_id,
            course_id=course_id,
        )
        if existing is not None:
            return False

        self.session.add(UserCourse(user_id=user_id, course_id=course_id))
        await self.session.flush()
        return True

    async def count_course_enrollments(self, course_id: int) -> int:
        stmt = select(func.count(UserCourse.user_id)).where(
            UserCourse.course_id == course_id,
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def delete_course(self, course: Course) -> None:
        await self.session.delete(course)
        await self.session.flush()

    async def delete_user_course_data(
        self,
        user_id: int,
        course_id: int,
    ) -> None:
        subtopic_ids = (
            select(Subtopic.id)
            .join(Topic, Topic.id == Subtopic.topic_id)
            .where(Topic.course_id == course_id)
        )

        await self.session.execute(
            delete(SubtopicProgress).where(
                SubtopicProgress.user_id == user_id,
                SubtopicProgress.subtopic_id.in_(subtopic_ids),
            )
        )
        await self.session.execute(
            delete(CourseProgress).where(
                CourseProgress.user_id == user_id,
                CourseProgress.course_id == course_id,
            )
        )
        await self.session.execute(
            delete(Test).where(
                Test.user_id == user_id,
                Test.course_id == course_id,
            )
        )
        await self.session.execute(
            delete(UserCourse).where(
                UserCourse.user_id == user_id,
                UserCourse.course_id == course_id,
            )
        )
        await self.session.flush()
