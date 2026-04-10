from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends

from core.di.providers.auth import RequireRoles
from models.user import RoleEnum
from schemas.auth import UserFromToken
from schemas.course import CourseCreateSchema, CourseReadSchema
from services.course import CourseService

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