from dataclasses import dataclass
from typing import Protocol

from pydantic import BaseModel


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


class GeneratedTestQuestionSchema(BaseModel):
    text: str
    options: list[str]
    correct_option_index: int


class GeneratedTestSchema(BaseModel):
    topic: str
    questions: list[GeneratedTestQuestionSchema]
