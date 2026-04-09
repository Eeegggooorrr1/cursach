import asyncio

from main import container
from .seed_service import SeedService


async def _load_seed() -> None:
    async with container() as c:
        service = await c.get(SeedService)
        await service.load_data()


def load_seed() -> None:
    asyncio.run(_load_seed())
