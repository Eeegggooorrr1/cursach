from dataclasses import dataclass

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.user import User
from schemas.user import (
    UserCreateSchema,
    UserUpdateSchema,
)


@dataclass
class UserRepository:
    session: AsyncSession

    async def create_user(self, user_data: UserCreateSchema) -> User:
        data = user_data.model_dump(exclude_unset=True, exclude_none=True)
        user = User(**data)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def find_user_by_email(self, email: EmailStr) -> User | None:
        stmt = (
            select(User)
            .filter_by(email=email)
            .options(selectinload(User.role))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_user_by_id(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .filter_by(id=user_id)
            .options(selectinload(User.role))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user(
        self, user_id: int, user_data: UserUpdateSchema
    ) -> User | None:
        user = await self.find_user_by_id(user_id)
        if user is None:
            return None

        data = user_data.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(user, field, value)

        await self.session.flush()
        return user

    async def delete_user(self, user_id: int) -> bool:
        user = await self.find_user_by_id(user_id)
        if user is None:
            return False

        await self.session.delete(user)
        await self.session.flush()
        return True
