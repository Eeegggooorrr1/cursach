from dishka import provide, Scope, Provider
from openai import AsyncOpenAI

from ai.contracts import LLMClient
from ai.deepseek import DeepSeekClient
from ai.prompts.test_generation.factory import \
    TestGenerationPromptFactory
from core.config import Settings


class AIProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def test_prompt_factory(self) -> TestGenerationPromptFactory:
        return TestGenerationPromptFactory()

    @provide(scope=Scope.APP)
    def deepseek_openai_client(self, settings: Settings) -> AsyncOpenAI:
        return AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_URL,
        )

    @provide(scope=Scope.REQUEST)
    def llm_client(
        self,
        deepseek_openai_client: AsyncOpenAI,
        settings: Settings,
    ) -> LLMClient:
        return DeepSeekClient(
            client=deepseek_openai_client,
            model=settings.DEEPSEEK_MODEL,
        )