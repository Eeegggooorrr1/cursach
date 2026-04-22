from datetime import datetime, timezone

from sqlalchemy import select, update as sa_update, ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from models.refresh_token import RefreshToken


class RefreshTokenRepository:
    model = RefreshToken

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_token(self, token: str) -> RefreshToken | None:
        stmt = select(self.model).where(self.model.token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _revoke_where(self, condition: ColumnElement[bool]) -> None:
        stmt = (
            sa_update(self.model)
            .where(condition)
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def revoke_all_for_user(self, user_id: int) -> None:
        await self._revoke_where(self.model.user_id == user_id)

    async def revoke_by_token(self, token: str) -> None:
        await self._revoke_where(self.model.token == token)

    async def create_and_revoke_all_for_user(
        self,
        new_token: str,
        user_id: int,
        expires_at: datetime,
    ) -> None:
        await self.revoke_all_for_user(user_id)
        self.session.add(
            self.model(
                user_id=user_id,
                token=new_token,
                expires_at=expires_at,
            )
        )
        await self.session.flush()

    async def rotate_token(
        self,
        old_token: str,
        new_token: str,
        user_id: int,
        expires_at: datetime,
    ) -> None:
        self.session.add(
            self.model(
                user_id=user_id,
                token=new_token,
                expires_at=expires_at,
            )
        )
        await self.session.flush()
        await self.revoke_by_token(old_token)
