import json
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import Settings


@dataclass
class SeedService:
    session: AsyncSession
    settings: Settings

    async def load_data(self) -> None:
        directory = Path(self.settings.SEED_DIR)

        if not directory.exists():
            raise ValueError(f"Seed directory not found: {directory}")

        for file_path in sorted(directory.glob("*.json")):
            payload = json.loads(file_path.read_text(encoding="utf-8"))

            for item in payload:
                await self._upsert_item(item)

    @staticmethod
    def _import_string(path: str):
        module_path, attr_name = path.rsplit(".", 1)
        module = import_module(module_path)
        return getattr(module, attr_name)

    async def _upsert_item(self, item: Any) -> None:
        model = self._import_string(item["model"])
        values = dict(item.get("fields", {}))
        lookup_fields = item.get("lookup", [])

        if "id" in item:
            values["id"] = item["id"]

        if lookup_fields:
            obj = await self._find_by_lookup(
                model=model,
                values=values,
                lookup_fields=lookup_fields,
            )
            if obj is None:
                self.session.add(model(**values))
                return

            for field, value in values.items():
                setattr(obj, field, value)
            return

        await self.session.merge(model(**values))

    async def _find_by_lookup(
        self,
        model,
        values: dict[str, Any],
        lookup_fields: list[str],
    ):
        conditions = []
        for field in lookup_fields:
            if field not in values:
                raise ValueError(f"Lookup field is missing in seed item: {field}")
            conditions.append(getattr(model, field) == values[field])

        stmt = select(model).where(*conditions)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
