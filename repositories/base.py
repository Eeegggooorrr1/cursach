from __future__ import annotations

from typing import Any, Generic, TypeVar
from models.base import Base
from pydantic import BaseModel
from sqlalchemy import delete as sa_delete, select
from sqlalchemy.ext.asyncio import AsyncSession

TModel = TypeVar("TModel", bound=Base)
TCreate = TypeVar("TCreate", bound=BaseModel)
TUpdate = TypeVar("TUpdate", bound=BaseModel)
TFilter = TypeVar("TFilter", bound=BaseModel)


class BaseRepository(Generic[TModel, TCreate, TUpdate, TFilter]):
    model: type[TModel]

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _dump(dto: BaseModel | None, *, exclude_none: bool = False) -> dict[str, Any]:
        if dto is None:
            return {}
        return dto.model_dump(exclude_unset=True, exclude_none=exclude_none)

    async def find_by_id(self, data_id: int) -> TModel | None:
        stmt = select(self.model).where(self.model.id == data_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_one(self, filters: TFilter) -> TModel | None:
        filter_dict = self._dump(filters, exclude_none=True)
        if not filter_dict:
            raise ValueError("filters must not be empty")

        stmt = select(self.model).filter_by(**filter_dict)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all(self, filters: TFilter | None = None) -> list[TModel]:
        stmt = select(self.model)

        filter_dict = self._dump(filters, exclude_none=True)
        if filter_dict:
            stmt = stmt.filter_by(**filter_dict)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, values: TCreate) -> TModel:
        data = self._dump(values, exclude_none=True)
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update_by_id(self, data_id: int, values: TUpdate) -> TModel | None:
        instance = await self.find_by_id(data_id)
        if instance is None:
            return None

        data = self._dump(values, exclude_none=True)
        for field, value in data.items():
            setattr(instance, field, value)

        await self.session.flush()
        return instance

    async def delete_by_id(self, data_id: int) -> bool:
        instance = await self.find_by_id(data_id)
        if instance is None:
            return False

        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def delete(self, filters: TFilter) -> int:
        filter_dict = self._dump(filters, exclude_none=True)
        if not filter_dict:
            raise ValueError("filters must not be empty")

        stmt = sa_delete(self.model).filter_by(**filter_dict)
        result = await self.session.execute(stmt)
        return result.rowcount or 0
