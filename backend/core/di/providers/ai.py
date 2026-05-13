from dishka import provide, Scope, Provider
from jinja2 import Environment
from openai import AsyncOpenAI

from ai.contracts import LLMClient
from ai.deepseek import DeepSeekClient
from ai.factories.course_generation_factory import (
    CourseGenerationPromptFactory,
)
from ai.factories.test_generation_factory import \
    TestGenerationPromptFactory
from core.ai import create_deepseek_openai_client, create_prompt_environment
from core.config import Settings


class AIProvider(Provider):

    @provide(scope=Scope.APP)
    def jinja_env(self) -> Environment:
        return create_prompt_environment()

    @provide(scope=Scope.REQUEST)
    def test_prompt_factory(
        self, env: Environment
    ) -> TestGenerationPromptFactory:
        return TestGenerationPromptFactory(env=env)

    @provide(scope=Scope.REQUEST)
    def course_prompt_factory(
        self, env: Environment
    ) -> CourseGenerationPromptFactory:
        return CourseGenerationPromptFactory(env=env)

    @provide(scope=Scope.APP)
    def deepseek_openai_client(self, settings: Settings) -> AsyncOpenAI:
        return create_deepseek_openai_client(settings)

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
