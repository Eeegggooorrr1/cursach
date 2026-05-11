from collections import deque
from dataclasses import dataclass, field


@dataclass
class FakeLLMClient:
    responses: deque[str] = field(default_factory=deque)
    calls: list[dict] = field(default_factory=list)

    def enqueue(self, response: str) -> None:
        self.responses.append(response)

    async def complete(
        self,
        system: str,
        user: str,
        temperature: float = 0.0,
    ) -> str:
        self.calls.append(
            {
                "system": system,
                "user": user,
                "temperature": temperature,
            }
        )
        if not self.responses:
            raise AssertionError("FakeLLMClient has no queued response")
        return self.responses.popleft()
