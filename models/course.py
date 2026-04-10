from sqlalchemy import ForeignKey, Index, Integer, String, Text, \
    DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

class Course(Base):

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    topics: Mapped[list["Topic"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )
    user: Mapped["User"] = relationship("User",
                                        back_populates="courses")

class Topic(Base):

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)

    course: Mapped[Course] = relationship(back_populates="topics")
    subtopics: Mapped[list["Subtopic"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
    )

class Subtopic(Base):

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)

    topic: Mapped[Topic] = relationship(back_populates="subtopics")
