from dataclasses import dataclass
from typing import Any

from models.course import Subtopic
from models.progress import SubtopicProgress


@dataclass(frozen=True)
class TestQuestionCountPolicy:
    min_questions: int = 10
    max_questions: int = 24

    def build_subtopic_plan(
        self,
        subtopics: list[Subtopic],
        progress_by_subtopic_id: dict[int, SubtopicProgress],
        test_no: int,
    ) -> list[dict[str, Any]]:
        if not subtopics:
            return []

        selected_subtopics = self._select_subtopics(
            subtopics=subtopics,
            test_no=test_no,
        )
        total_questions = min(
            self.max_questions,
            max(self.min_questions, len(selected_subtopics)),
        )
        extra_questions = total_questions - len(selected_subtopics)

        plan = [
            {
                "name": subtopic.name,
                "difficulty": self._difficulty_for(
                    subtopic=subtopic,
                    progress_by_subtopic_id=progress_by_subtopic_id,
                ),
                "questions_count": 1,
            }
            for subtopic in selected_subtopics
        ]

        weighted_indexes = sorted(
            range(len(plan)),
            key=lambda index: (-plan[index]["difficulty"], index),
        )

        """
        Базово каждая выбранная подтема получает один вопрос. Остаток
        распределяем по кругу, начиная с более сложных подтем,
        т.е. тест сильнее фокусируется на
        участках, где пользователю потенциально нужнее проверка.
        """

        for index in range(extra_questions):
            plan[weighted_indexes[index % len(weighted_indexes)]][
                "questions_count"
            ] += 1

        return plan

    def _select_subtopics(
        self,
        subtopics: list[Subtopic],
        test_no: int,
    ) -> list[Subtopic]:
        if len(subtopics) <= self.max_questions:
            return subtopics

        start = ((test_no - 1) * self.max_questions) % len(subtopics)
        rotated = subtopics[start:] + subtopics[:start]
        return rotated[: self.max_questions]

    @staticmethod
    def _difficulty_for(
        subtopic: Subtopic,
        progress_by_subtopic_id: dict[int, SubtopicProgress],
    ) -> int:
        progress = progress_by_subtopic_id.get(subtopic.id)
        return progress.current_difficulty if progress is not None else 0
