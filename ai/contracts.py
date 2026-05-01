from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Prompt:
    system: str
    user: str


class LLMClient(Protocol):
    async def complete(
        self,
        system: str,
        user: str,
        temperature: float = 0.0,
    ) -> str: ...
