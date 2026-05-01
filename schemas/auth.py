from pydantic import EmailStr

from models.user import RoleEnum
from schemas.base import StrictSchema


class UserFromToken(StrictSchema):
    id: int
    username: str
    role: RoleEnum


class UserLoginSchema(StrictSchema):
    email: EmailStr
    password: str


class UserRegisterSchema(StrictSchema):
    email: EmailStr
    password: str
    username: str
