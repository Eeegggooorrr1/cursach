from pydantic import (
    EmailStr,
)

from models.user import RoleEnum
from schemas.base import StrictSchema


class UserCreateSchema(StrictSchema):
    email: EmailStr
    username: str
    password: str
    role: RoleEnum | None = None


class UserUpdateSchema(StrictSchema):
    username: str | None = None


class UserFilterSchema(StrictSchema):
    email: EmailStr | None = None
    username: str | None = None
