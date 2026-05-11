from sqlalchemy.ext.asyncio import AsyncEngine

import models.course
import models.progress
import models.refresh_token
import models.test
import models.user
from models.base import Base


async def upgrade(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def downgrade(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
