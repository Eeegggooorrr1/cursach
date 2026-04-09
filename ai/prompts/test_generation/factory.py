from dataclasses import dataclass
from importlib import resources

from ai.contracts import Prompt


@dataclass(frozen=True)
class TestGenerationPromptFactory:

    @staticmethod
    def _read(filename: str) -> str:
        package = f"ai.prompts.test_generation"
        return resources.files(package).joinpath(filename).read_text(encoding="utf-8")

    def build(
        self,
        topic: str,
        questions_count: int,
        options_count: int,
    ) -> Prompt:
        system_template = self._read("system.txt")
        user_template = self._read("user.txt")

        system = system_template \
            .replace("{questions_count}", str(questions_count)) \
            .replace("{options_count}", str(options_count))

        user = user_template \
            .replace("{topic}", topic) \
            .replace("{questions_count}", str(questions_count)) \
            .replace("{options_count}", str(options_count))

        return Prompt(
            system=system,
            user=user,
        )