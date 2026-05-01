from dataclasses import dataclass


@dataclass(frozen=True)
class PreparedQuestionData:
    subtopic_id: int
    prompt: str
    options: list[str]
    correct_option_index: int

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

        if not (0 <= self.correct_option_index < len(normalized_options)):
            raise ValueError("correct_option_index out of range")

        object.__setattr__(self, "options", normalized_options)
        object.__setattr__(self, "prompt", self.prompt.strip())


@dataclass(frozen=True)
class QuestionAttemptDraft:
    question_id: int
    selected_option_id: int
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
