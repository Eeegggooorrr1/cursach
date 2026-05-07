from jinja2 import Environment, PackageLoader
from openai import AsyncOpenAI

from core.config import Settings


def create_prompt_environment() -> Environment:
    return Environment(
        loader=PackageLoader("ai"),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def create_deepseek_openai_client(settings: Settings) -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_URL,
    )
