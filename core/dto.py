from dataclasses import dataclass


@dataclass(frozen=True)
class PreparedQuestionData:
    subtopic_id: int
    prompt: str
    options: list[str]
    correct_option_indexes: list[int]
    is_multiple_choice: bool = False

    def __post_init__(self):
        if not self.prompt.strip():
            raise ValueError("Question prompt must not be empty")

        if len(self.options) < 2:
            raise ValueError("Question must have at least two options")

        normalized_options = [opt.strip() for opt in self.options]

        if any(not opt for opt in normalized_options):
            raise ValueError("Options must not contain empty values")

        if len(set(normalized_options)) != len(normalized_options):
            raise ValueError("Options must be unique")

        correct_indexes = list(self.correct_option_indexes)
        if len(set(correct_indexes)) != len(correct_indexes):
            raise ValueError("Correct option indexes must be unique")

        if any(
            index < 0 or index >= len(normalized_options)
            for index in correct_indexes
        ):
            raise ValueError("correct_option_indexes out of range")

        if self.is_multiple_choice:
            if len(correct_indexes) < 2:
                raise ValueError(
                    "Multiple choice question must have at least two correct options"
                )
        elif len(correct_indexes) != 1:
            raise ValueError(
                "Single choice question must have exactly one correct option"
            )

        object.__setattr__(self, "options", normalized_options)
        object.__setattr__(self, "prompt", self.prompt.strip())
        object.__setattr__(self, "correct_option_indexes", correct_indexes)


@dataclass(frozen=True)
class QuestionAttemptDraft:
    question_id: int
    selected_option_ids: list[int]
    is_correct: bool


@dataclass(frozen=True)
class SubtopicProgressUpdate:
    subtopic_id: int
    mastery_score: float
    current_difficulty: int
    current_streak: int


@dataclass(frozen=True)
class SubmissionEvaluationResult:
    attempts: list[QuestionAttemptDraft]
    subtopic_updates: list[SubtopicProgressUpdate]
    correct_count: int
    incorrect_count: int
