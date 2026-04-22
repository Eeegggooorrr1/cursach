from pydantic import (
    BaseModel,
    EmailStr,
)

from models.user import RoleEnum


class UserCreateSchema(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: RoleEnum | None = None


class UserUpdateSchema(BaseModel):
    username: str | None = None


class UserFilterSchema(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
