from dataclasses import dataclass

from fastapi import Response

from core.auth.tokens import ACCESS_TOKEN_COOKIE, REFRESH_TOKEN_COOKIE


@dataclass
class CookieManager:

    @staticmethod
    def _set_access_token(response: Response, access_token: str):
        response.set_cookie(
            key=ACCESS_TOKEN_COOKIE,
            value=access_token,
            httponly=False,
            secure=False,
            samesite="lax",
        )

    @staticmethod
    def _set_refresh_token(response: Response, refresh_token: str):
        response.set_cookie(
            key=REFRESH_TOKEN_COOKIE,
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
        )

    def set_auth_cookies(
        self, response: Response, access_token: str, refresh_token: str
    ):
        self._set_access_token(response, access_token)
        self._set_refresh_token(response, refresh_token)
