from dataclasses import dataclass
from importlib import resources

from jinja2 import Environment

from ai.contracts import Prompt


@dataclass(frozen=True)
class TestGenerationPromptFactory:
    env: Environment

    def build(
        self,
        topic: str,
        questions_count: int,
        options_count: int,
    ) -> Prompt:
        system = self.env.get_template("test_generation/system.txt").render(
            questions_count=questions_count,
            options_count=options_count,
        )
        user = self.env.get_template("test_generation/user.txt").render(
            topic=topic,
            questions_count=questions_count,
            options_count=options_count,
        )
        return Prompt(system=system, user=user)
