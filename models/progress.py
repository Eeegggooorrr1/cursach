from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
    Float,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from models.base import Base


class TestProgressStatusEnum(str, Enum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"

class CourseProgressStatusEnum(str, Enum):
    ACTIVE = "active"
    FINISHED = "finished"

class CourseProgress(Base):
    __tablename__ = "course_progress"

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String, nullable=False, default=CourseProgressStatusEnum.ACTIVE
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class TestProgress(Base):
    __tablename__ = "test_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    test_id: Mapped[int] = mapped_column(
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    correct_percentage: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    status: Mapped[str] = mapped_column(
        String, nullable=False, default=TestProgressStatusEnum.IN_PROGRESS
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "test_id", name="uq_test_progress_user_test"
        ),
    )


class SubtopicProgress(Base):
    __tablename__ = "subtopic_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subtopic_id: Mapped[int] = mapped_column(
        ForeignKey("subtopics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    mastery_score: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    current_difficulty: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    current_streak: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "subtopic_id", name="uq_subtopic_progress_user_subtopic"
        ),
    )


class QuestionAttempt(Base):
    __tablename__ = "question_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_test_progress_id: Mapped[int] = mapped_column(
        ForeignKey("test_progress.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    selected_option_id: Mapped[int | None] = mapped_column(
        ForeignKey("answer_options.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_correct: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "course_test_progress_id",
            "question_id",
            name="uq_attempt_progress_question",
        ),
    )
