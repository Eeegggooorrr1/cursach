from dataclasses import dataclass
from enum import IntEnum

from pydantic import BaseModel, Field, ConfigDict, model_validator


class TestCreateSchema(BaseModel):
    topic: str
    questions_count: int = Field(ge=1, le=20)
    options_count: int = Field(ge=2, le=8)


class TestOptionReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: int
    text: str


class TestQuestionReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    subtopic_id: int
    prompt: str
    options: list[TestOptionReadSchema] = Field(
        validation_alias="answer_options",
    )


class TestReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    course_id: int
    position: int
    title: str
    questions: list[TestQuestionReadSchema]


class SubmitAnswerSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: int
    selected_option_id: int


class TestSubmitSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answers: list[SubmitAnswerSchema] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_questions(self):
        question_ids = [item.question_id for item in self.answers]
        if len(set(question_ids)) != len(question_ids):
            raise ValueError("duplicate question_id in submit payload")
        return self


class TestSubmitResponseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    test_progress_id: int
    test_id: int
    status: str
    correct_percentage: float


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


class Difficulty(IntEnum):
    EASY = 0
    MEDIUM = 1
    HARD = 2
