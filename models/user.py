from enum import Enum

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class RoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"


class Role(Base):

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=False
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class User(Base):

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )

    email: Mapped[str]
    password: Mapped[str]
    username: Mapped[str]
    profile_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"), nullable=False, default=1
    )

    role: Mapped["Role"] = relationship("Role", lazy="selectin")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    courses: Mapped[list["Course"]] = relationship(
        "Course",
        secondary="user_courses",
        back_populates="users",
    )

    created_courses: Mapped[list["Course"]] = relationship(
        "Course",
        back_populates="creator",
        foreign_keys="Course.creator_id",
    )

    tests: Mapped[list["Test"]] = relationship(
        "Test",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserCourse(Base):

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True,
    )
