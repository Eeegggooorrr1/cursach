from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends

from core.di.providers.auth import RequireRoles
from models.user import RoleEnum
from schemas.auth import UserFromToken
from schemas.test import TestCreateSchema, TestReadSchema
from services.test import TestService

router = APIRouter(prefix="/tests", tags=["tests"], route_class=DishkaRoute)


@router.post("/")
async def create_test(
    test: TestCreateSchema,
    test_service: FromDishka[TestService],
    user: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
) -> TestReadSchema:
    created_test = await test_service.create_test(
        topic=test.topic,
        questions_count=test.questions_count,
        options_count=test.options_count,
        user_id=user.id,
    )

    return created_test
