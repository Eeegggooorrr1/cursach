from typing import Annotated

from pydantic import EmailStr, Field, StringConstraints

from models.user import RoleEnum
from schemas.base import OrmSchema, StrictSchema
from schemas.validation import (
    PROFILE_DESCRIPTION_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
)


class UserCreateSchema(StrictSchema):
    email: EmailStr
    username: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=USERNAME_MIN_LENGTH,
            max_length=USERNAME_MAX_LENGTH,
        ),
    ]
    password: str
    profile_description: Annotated[
        str,
        Field(max_length=PROFILE_DESCRIPTION_MAX_LENGTH),
    ] | None = None
    role: RoleEnum | None = None


class UserUpdateSchema(StrictSchema):
    profile_description: Annotated[
        str,
        Field(max_length=PROFILE_DESCRIPTION_MAX_LENGTH),
    ] | None = None


class UserFilterSchema(StrictSchema):
    email: EmailStr | None = None
    username: str | None = None


class UserProfileSchema(OrmSchema):
    id: int
    email: EmailStr
    username: str
    profile_description: str | None
    is_blocked: bool
    role: str
