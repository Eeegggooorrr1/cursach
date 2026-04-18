from dataclasses import dataclass
from importlib import resources
from typing import Any

from jinja2 import Environment

from ai.contracts import Prompt


@dataclass(frozen=True)
class TestGenerationPromptFactory:
    env: Environment

    def build(
        self,
        course_title: str,
        course_comment: str | None,
        test_no: int,
        subtopics: list[dict[str, Any]],
        recent_tests_questions: list[str],
        options_count: int = 3,
    ) -> Prompt:
        """
        [
            {
                "name": str,
                "difficulty": int,
                "questions_count": int,
            }
        ]
        """

        if not subtopics:
            raise ValueError("subtopics must not be empty")

        normalized_subtopics = [
            {
                "name": str(item["name"]).strip(),
                "difficulty": int(item.get("difficulty", 0)),
                "questions_count": int(item["questions_count"]),
            }
            for item in subtopics
        ]

        total_questions = sum(item["questions_count"] for item in normalized_subtopics)

        subtopics_block = self._render_subtopics_block(normalized_subtopics)

        recent_questions_block = self._render_recent_questions_block(
            recent_tests_questions
        )

        system = self.env.get_template("test_generation/system.txt").render(
            questions_count=total_questions,
            options_count=options_count,
        )

        user = self.env.get_template("test_generation/user.txt").render(
            topic=course_title.strip(),
            course_comment=(course_comment or "").strip(),
            test_no=test_no,
            questions_count=total_questions,
            options_count=options_count,
            subtopics=subtopics_block,
            recent_tests_questions=recent_questions_block,
        )

        return Prompt(system=system, user=user)

    @staticmethod
    def _render_subtopics_block(subtopics: list[dict[str, Any]]) -> str:

        lines: list[str] = []

        for item in subtopics:
            lines.append(
                f'- {item["name"]} | difficulty={item["difficulty"]} | questions={item["questions_count"]}'
            )

        return "\n".join(lines)

    @staticmethod
    def _render_recent_questions_block(questions: list[str]) -> str:
        if not questions:
            return "[]"

        cleaned = [
            " ".join(q.strip().split())
            for q in questions
            if q and q.strip()
        ]

        if not cleaned:
            return "[]"

        return "\n".join(f"- {q}" for q in cleaned)