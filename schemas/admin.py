from datetime import datetime

from pydantic import EmailStr

from schemas.base import StrictSchema
from schemas.course import PaginationSchema


class AdminUserSchema(StrictSchema):
    id: int
    email: EmailStr
    username: str
    profile_description: str | None
    is_blocked: bool
    role: str


class AdminCourseSchema(StrictSchema):
    id: int
    creator_id: int
    creator_email: EmailStr
    creator_username: str
    title: str
    comment: str | None
    is_public: bool
    is_public_allowed: bool
    created_at: datetime


class PaginatedAdminUserListSchema(StrictSchema):
    items: list[AdminUserSchema]
    meta: PaginationSchema


class PaginatedAdminCourseListSchema(StrictSchema):
    items: list[AdminCourseSchema]
    meta: PaginationSchema
