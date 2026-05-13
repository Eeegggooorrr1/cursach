from dataclasses import dataclass
from typing import Any, ClassVar

from jinja2 import Environment

from ai.contracts import Prompt


@dataclass(frozen=True)
class TestGenerationPromptFactory:
    env: Environment

    DIFFICULTY_GUIDANCE: ClassVar[dict[int, tuple[str, str]]] = {
        0: (
            "basic",
            "recognition, definitions, direct facts, one-step questions",
        ),
        1: (
            "applied",
            "practical use, comparisons, short scenarios, plausible distractors",
        ),
        2: (
            "advanced",
            "analysis, edge cases, debugging, consequences, multi-step reasoning",
        ),
    }

    def build(
        self,
        course_title: str,
        course_prompt: str | None,
        test_no: int,
        subtopics: list[dict[str, Any]],
        recent_tests_questions: list[str],
        single_choice_options_range: tuple[int, int] = (2, 6),
        multiple_choice_options_range: tuple[int, int] = (3, 9),
    ) -> Prompt:

        if not subtopics:
            raise ValueError("subtopics must not be empty")

        normalized_subtopics = [
            {
                "name": str(item["name"]).strip(),
                "difficulty": self._normalize_difficulty(
                    item.get("difficulty", 0),
                ),
                "questions_count": int(item["questions_count"]),
            }
            for item in subtopics
        ]

        total_questions = sum(
            item["questions_count"] for item in normalized_subtopics
        )

        subtopics_block = self._render_subtopics_block(normalized_subtopics)

        recent_questions_block = self._render_recent_questions_block(
            recent_tests_questions
        )

        system = self.env.get_template("test_generation/system.txt").render(
            topic=course_title.strip(),
            course_prompt=(course_prompt or "").strip(),
            test_no=test_no,
            questions_count=total_questions,
            difficulty_rubric=self._render_difficulty_rubric(),
            single_choice_options_range=self._format_range(
                single_choice_options_range,
            ),
            multiple_choice_options_range=self._format_range(
                multiple_choice_options_range,
            ),
            subtopics=subtopics_block,
            recent_tests_questions=recent_questions_block,
        )

        user = self.env.get_template("test_generation/user.txt").render(
            topic=course_title.strip(),
            course_prompt=(course_prompt or "").strip(),
            test_no=test_no,
            questions_count=total_questions,
            difficulty_rubric=self._render_difficulty_rubric(),
            single_choice_options_range=self._format_range(
                single_choice_options_range,
            ),
            multiple_choice_options_range=self._format_range(
                multiple_choice_options_range,
            ),
            subtopics=subtopics_block,
            recent_tests_questions=recent_questions_block,
        )

        return Prompt(system=system, user=user)

    @staticmethod
    def _render_subtopics_block(subtopics: list[dict[str, Any]]) -> str:

        lines: list[str] = []

        for item in subtopics:
            level, target = TestGenerationPromptFactory.DIFFICULTY_GUIDANCE[
                item["difficulty"]
            ]
            lines.append(
                f'- {item["name"]} | level={level} | target={target} | questions={item["questions_count"]}'
            )

        return "\n".join(lines)

    @staticmethod
    def _render_recent_questions_block(questions: list[str]) -> str:
        if not questions:
            return "[]"

        cleaned = [
            " ".join(q.strip().split()) for q in questions if q and q.strip()
        ]

        if not cleaned:
            return "[]"

        return "\n".join(f"- {q}" for q in cleaned)

    @staticmethod
    def _format_range(value: tuple[int, int]) -> str:
        return f"{value[0]}-{value[1]}"

    @staticmethod
    def _normalize_difficulty(value: Any) -> int:
        difficulty = int(value)
        return max(0, min(2, difficulty))

    @classmethod
    def _render_difficulty_rubric(cls) -> str:
        return "\n".join(
            f"- {level}: {target}"
            for _, (level, target) in cls.DIFFICULTY_GUIDANCE.items()
        )
