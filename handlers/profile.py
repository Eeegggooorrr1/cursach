from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends

from core.auth import RequireRoles
from models.user import RoleEnum
from schemas.auth import UserFromToken
from schemas.user import UserProfileSchema, UserUpdateSchema
from services.user import UserService

router = APIRouter(
    prefix="/profile", tags=["profile"], route_class=DishkaRoute
)


@router.patch(
    "/",
    description="Обновить описание своего профиля",
)
async def update_user(
    user_update_data: UserUpdateSchema,
    user_data: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
    user_service: FromDishka[UserService],
) -> UserProfileSchema:
    return await user_service.update_profile(
        user_id=user_data.id,
        payload=user_update_data,
    )


@router.get("/", description="Получить свой профиль")
async def get_me(
    user_data: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
    user_service: FromDishka[UserService],
) -> UserProfileSchema:
    return await user_service.get_profile(user_id=user_data.id)
