from pydantic import BaseModel, EmailStr

from models.user import RoleEnum


class UserFromToken(BaseModel):
    id: int
    username: str
    role: RoleEnum


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str
    username: str
