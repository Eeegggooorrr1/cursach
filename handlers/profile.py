from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status

from core.di.providers.auth import RequireRoles
from models.user import RoleEnum
from repositories.user import UserRepository
from schemas.auth import UserFromToken
from schemas.user import UserUpdateSchema

router = APIRouter(
    prefix="/profile", tags=["profile"], route_class=DishkaRoute
)


@router.patch(
    "/",
    description="редачим свой профиль (поля по которым был вериф акка)",
)
async def update_user(
    user_update_data: UserUpdateSchema,
    user_data: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
    user_repository: FromDishka[UserRepository],
):
    user = await user_repository.update_user(
        user_id=user_data.id, user_data=user_update_data
    )
    return user


@router.get("/", description="глянуть свой профиль")
async def get_me(
    user_data: Annotated[
        UserFromToken, Depends(RequireRoles(RoleEnum.USER, RoleEnum.ADMIN))
    ],
    user_repository: FromDishka[UserRepository],
):
    user = await user_repository.find_user_by_id(user_id=user_data.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
