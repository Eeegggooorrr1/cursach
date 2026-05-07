from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Response
from fastapi.security import HTTPBearer

from core.auth import RefreshToken
from schemas.auth import UserLoginSchema, UserRegisterSchema
from services.auth import AuthService
from services.cookie import CookieManager
from services.security import SecurityService

router = APIRouter(prefix="/auth", tags=["auth"], route_class=DishkaRoute)
security = HTTPBearer(auto_error=True)


@router.post(
    "/login",
)
async def login(
    response: Response,
    user: UserLoginSchema,
    auth_service: FromDishka[AuthService],
    cookie_manager: FromDishka[CookieManager],
) -> dict[str, str]:

    access_token, refresh_token = await auth_service.login(
        user.email, user.password
    )

    cookie_manager.set_auth_cookies(response, access_token, refresh_token)

    return {"msg": "ok"}


@router.post(
    "/register",
)
async def register(
    response: Response,
    user: UserRegisterSchema,
    auth_service: FromDishka[AuthService],
    cookie_manager: FromDishka[CookieManager],
) -> dict[str, str]:

    access_token, refresh_token = await auth_service.register(
        user.email,
        user.password,
        user.username,
        user.profile_description,
    )

    cookie_manager.set_auth_cookies(response, access_token, refresh_token)

    return {"msg": "ok"}


@router.post(
    "/refresh",
    description="если access протухший/отсутствует, то идем сюда",
)
async def refresh_tokens(
    response: Response,
    refresh_token: FromDishka[RefreshToken],
    security_service: FromDishka[SecurityService],
    cookie_manager: FromDishka[CookieManager],
):
    access_token, new_refresh_token = await security_service.refresh_tokens(
        refresh_token
    )
    cookie_manager.set_auth_cookies(response, access_token, new_refresh_token)

    return {"msg": "ok"}
