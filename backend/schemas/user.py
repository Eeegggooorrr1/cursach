from pydantic import (
    EmailStr,
    model_validator,
)

from models.user import RoleEnum
from schemas.base import OrmSchema, StrictSchema


class UserCreateSchema(StrictSchema):
    email: EmailStr
    username: str
    password: str
    profile_description: str | None = None
    role: RoleEnum | None = None

    @model_validator(mode="after")
    def normalize_user(self):
        self.username = self.username.strip()
        if not self.username:
            raise ValueError("username cannot be empty")
        return self


class UserUpdateSchema(StrictSchema):
    profile_description: str | None = None


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
