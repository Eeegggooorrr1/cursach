from typing import Annotated

from pydantic import EmailStr, Field, StringConstraints

from models.user import RoleEnum
from schemas.base import StrictSchema
from schemas.validation import (
    AUTH_LOGIN_PASSWORD_MIN_LENGTH,
    AUTH_PASSWORD_MAX_LENGTH,
    AUTH_PASSWORD_MIN_LENGTH,
    PROFILE_DESCRIPTION_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
)


class UserFromToken(StrictSchema):
    id: int
    username: str
    role: RoleEnum
    is_blocked: bool = False


class UserLoginSchema(StrictSchema):
    email: EmailStr
    password: Annotated[
        str,
        Field(
            min_length=AUTH_LOGIN_PASSWORD_MIN_LENGTH,
            max_length=AUTH_PASSWORD_MAX_LENGTH,
        ),
    ]


class UserRegisterSchema(StrictSchema):
    email: EmailStr
    password: Annotated[
        str,
        Field(
            min_length=AUTH_PASSWORD_MIN_LENGTH,
            max_length=AUTH_PASSWORD_MAX_LENGTH,
        ),
    ]
    username: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=USERNAME_MIN_LENGTH,
            max_length=USERNAME_MAX_LENGTH,
        ),
    ]
    profile_description: Annotated[
        str,
        Field(max_length=PROFILE_DESCRIPTION_MAX_LENGTH),
    ] | None = None
