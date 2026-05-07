from typing import TypeVar

from fastapi import HTTPException
from starlette import status
from starlette.requests import Request


ACCESS_TOKEN_COOKIE = "user_access_token"
REFRESH_TOKEN_COOKIE = "user_refresh_token"


class AccessToken(str):
    pass


class RefreshToken(str):
    pass


TToken = TypeVar("TToken", AccessToken, RefreshToken)


def get_access_token(request: Request) -> AccessToken:
    return _get_cookie_token(
        request=request,
        cookie_name=ACCESS_TOKEN_COOKIE,
        token_type=AccessToken,
        missing_detail="Access token not found",
    )


def get_refresh_token(request: Request) -> RefreshToken:
    return _get_cookie_token(
        request=request,
        cookie_name=REFRESH_TOKEN_COOKIE,
        token_type=RefreshToken,
        missing_detail="Refresh token not found",
    )


def _get_cookie_token(
    *,
    request: Request,
    cookie_name: str,
    token_type: type[TToken],
    missing_detail: str,
) -> TToken:
    token = request.cookies.get(cookie_name)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=missing_detail,
        )
    return token_type(token)
