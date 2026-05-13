from dataclasses import dataclass

from jinja2 import Environment

from ai.contracts import Prompt


@dataclass(frozen=True)
class CourseGenerationPromptFactory:
    env: Environment

    def build(
        self,
        title: str,
        prompt: str | None,
        topics: list[str],
        subtopics_count: int,
    ) -> Prompt:
        system = self.env.get_template("course_generation/system.txt").render()
        user = self.env.get_template("course_generation/user.txt").render(
            title=title,
            prompt=prompt,
            topics=topics,
            subtopics_count=subtopics_count,
        )
        return Prompt(system=system, user=user)
