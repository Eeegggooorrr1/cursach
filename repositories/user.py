from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.user import User
from repositories.base import BaseRepository
from schemas.user import (
    UserCreateSchema,
    UserUpdateSchema,
    UserFilterSchema,
)


class UserRepository(
    BaseRepository[User, UserCreateSchema, UserUpdateSchema, UserFilterSchema]
):
    model = User

    async def create_user(self, user_data: UserCreateSchema) -> User:
        user = await self.add(user_data)
        await self.session.refresh(user)
        return user

    async def find_user_by_email(self, email: EmailStr) -> User | None:
        stmt = (
            select(self.model)
            .filter_by(email=email)
            .options(selectinload(User.role))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_user_by_id(self, user_id: int) -> User | None:
        stmt = (
            select(self.model)
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
        return await self.delete_by_id(user_id)
