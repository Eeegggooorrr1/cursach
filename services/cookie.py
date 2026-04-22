from dataclasses import dataclass

from fastapi import Response


@dataclass
class CookieManager:

    @staticmethod
    def _set_access_token(response: Response, access_token: str):
        response.set_cookie(
            key="user_access_token",
            value=access_token,
            httponly=False,
            secure=False,
            samesite="lax",
        )

    @staticmethod
    def _set_refresh_token(response: Response, refresh_token: str):
        response.set_cookie(
            key="user_refresh_token",
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
