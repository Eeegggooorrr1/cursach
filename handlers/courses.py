from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Path

from core.di.providers.auth import RequireRoles
from models.user import RoleEnum
from schemas.auth import UserFromToken
from schemas.course import CourseCreateSchema, CourseReadSchema
from schemas.test import TestReadSchema
from services.course import CourseService
from services.test import TestService

router = APIRouter(prefix="/courses", tags=["courses"], route_class=DishkaRoute)


@router.post("/")
async def create_course(
    course: CourseCreateSchema,
    user: Annotated[UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))],
    course_service: FromDishka[CourseService],
) -> CourseReadSchema:
    created_course = await course_service.create_course(
        user_id=user.id,
        title=course.title,
        comment=course.comment,
        topics=course.topics,
    )

    return created_course

@router.post("/{course_id}/create-test")
async def create_test(
    course_id: Annotated[int, Path(gt=0)],
    test_service: FromDishka[TestService],
    user: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
) -> TestReadSchema:
    return await test_service.create_test(course_id=course_id, user_id=user.id)