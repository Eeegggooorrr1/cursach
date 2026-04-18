from dishka import provide, Scope, Provider
from jinja2 import Environment, PackageLoader
from openai import AsyncOpenAI

from ai.contracts import LLMClient
from ai.deepseek import DeepSeekClient
from ai.factories.course_generation_factory import \
    CourseGenerationPromptFactory
from ai.factories.test_generation_factory import TestGenerationPromptFactory
from core.config import Settings


class AIProvider(Provider):

    @provide(scope=Scope.APP)
    def jinja_env(self) -> Environment:
        return Environment(
            loader=PackageLoader("ai"),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    @provide(scope=Scope.REQUEST)
    def test_prompt_factory(self, env: Environment) -> TestGenerationPromptFactory:
        return TestGenerationPromptFactory(env=env)

    @provide(scope=Scope.REQUEST)
    def course_prompt_factory(self, env: Environment) -> CourseGenerationPromptFactory:
        return CourseGenerationPromptFactory(env=env)

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
