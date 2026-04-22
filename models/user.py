from enum import Enum

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Integer,
    String,
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
        back_populates="user",
        cascade="all, delete-orphan",
    )
