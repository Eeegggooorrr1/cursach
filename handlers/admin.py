from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Query

from core.auth import RequireRoles
from models.user import RoleEnum
from schemas.admin import (
    AdminUserSchema,
    PaginatedAdminCourseListSchema,
    PaginatedAdminUserListSchema,
)
from schemas.auth import UserFromToken
from schemas.course import CourseDetailSchema
from services.admin import AdminService


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    route_class=DishkaRoute,
)


@router.get("/blocked-users")
async def get_blocked_users(
    user: Annotated[UserFromToken, Depends(RequireRoles(RoleEnum.ADMIN))],
    admin_service: FromDishka[AdminService],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginatedAdminUserListSchema:
    return await admin_service.get_blocked_users(
        limit=limit,
        offset=offset,
    )


@router.patch("/users/{user_id}/block")
async def block_user(
    user_id: int,
    user: Annotated[UserFromToken, Depends(RequireRoles(RoleEnum.ADMIN))],
    admin_service: FromDishka[AdminService],
) -> AdminUserSchema:
    return await admin_service.block_user(
        admin_id=user.id,
        user_id=user_id,
    )


@router.patch("/users/{user_id}/unblock")
async def unblock_user(
    user_id: int,
    user: Annotated[UserFromToken, Depends(RequireRoles(RoleEnum.ADMIN))],
    admin_service: FromDishka[AdminService],
) -> AdminUserSchema:
    return await admin_service.unblock_user(user_id=user_id)


@router.get("/restricted-courses")
async def get_restricted_courses(
    user: Annotated[UserFromToken, Depends(RequireRoles(RoleEnum.ADMIN))],
    admin_service: FromDishka[AdminService],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginatedAdminCourseListSchema:
    return await admin_service.get_restricted_courses(
        limit=limit,
        offset=offset,
    )


@router.patch("/courses/{course_id}/restrict-public")
async def restrict_course_public_access(
    course_id: int,
    user: Annotated[UserFromToken, Depends(RequireRoles(RoleEnum.ADMIN))],
    admin_service: FromDishka[AdminService],
) -> CourseDetailSchema:
    return await admin_service.restrict_course_public_access(
        admin_id=user.id,
        course_id=course_id,
    )


@router.patch("/courses/{course_id}/restore-public")
async def restore_course_public_access(
    course_id: int,
    user: Annotated[UserFromToken, Depends(RequireRoles(RoleEnum.ADMIN))],
    admin_service: FromDishka[AdminService],
) -> CourseDetailSchema:
    return await admin_service.restore_course_public_access(
        course_id=course_id,
    )
