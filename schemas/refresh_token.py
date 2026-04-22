from datetime import datetime

from pydantic import BaseModel


class RefreshTokenFilter(BaseModel):
    token: str | None = None
    user_id: int | None = None


class RefreshTokenUpdateSchema(BaseModel):
    revoked_at: datetime


class RefreshTokenCreateSchema(BaseModel):
    token: str
    user_id: int
    expires_at: datetime
    revoked_at: datetime | None = None
