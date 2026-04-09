from __future__ import annotations

from dataclasses import dataclass

from openai import AsyncOpenAI

from ai.contracts import LLMClient
from core.exceptions import InvalidLLMResponseError



@dataclass
class DeepSeekClient(LLMClient):
    client: AsyncOpenAI
    model: str

    async def complete(
        self,
        system: str,
        user: str,
        temperature: float = 0.0,
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        if not content:
            raise InvalidLLMResponseError()

        return content