from datetime import datetime

from schemas.base import StrictSchema


class RefreshTokenFilter(StrictSchema):
    token: str | None = None
    user_id: int | None = None


class RefreshTokenUpdateSchema(StrictSchema):
    revoked_at: datetime


class RefreshTokenCreateSchema(StrictSchema):
    token: str
    user_id: int
    expires_at: datetime
    revoked_at: datetime | None = None
