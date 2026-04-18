from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Counter

from pydantic import BaseModel, model_validator, ConfigDict, \
    field_validator, Field
from pydantic_core.core_schema import ValidationInfo


@dataclass(frozen=True)
class Prompt:
    system: str
    user: str


class LLMClient(Protocol):
    async def complete(
        self,
        system: str,
        user: str,
        temperature: float = 0.0,
    ) -> str: ...


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


class PromptSubtopicSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    difficulty: int = Field(ge=0)
    questions_count: int = Field(gt=0)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("name must be a string")
        value = _normalize_text(value)
        if not value:
            raise ValueError("name must not be empty")
        return value


class GeneratedQuestionSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subtopic: str = Field(min_length=1)
    text: str = Field(min_length=1)
    options: list[str] = Field(min_length=2)
    correct_option_index: int = Field(ge=0)

    @field_validator("subtopic", "text", mode="before")
    @classmethod
    def normalize_required_string(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("value must be a string")
        value = _normalize_text(value)
        if not value:
            raise ValueError("value must not be empty")
        return value

    @field_validator("options", mode="before")
    @classmethod
    def validate_options_raw(cls, value):
        if not isinstance(value, list):
            raise ValueError("options must be a list")
        cleaned: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError("each option must be a string")
            item = _normalize_text(item)
            if not item:
                raise ValueError("option must not be empty")
            cleaned.append(item)
        return cleaned

    @model_validator(mode="after")
    def validate_question(self, info: ValidationInfo):
        if len(set(self.options)) != len(self.options):
            raise ValueError("duplicated options in one question")

        if not 0 <= self.correct_option_index < len(self.options):
            raise ValueError("correct_option_index out of range")

        expected_options_count = (info.context or {}).get("options_count")
        if expected_options_count is not None and len(self.options) != expected_options_count:
            raise ValueError(f"each question must have exactly {expected_options_count} options")

        return self


class GeneratedTestSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic: str = Field(min_length=1)
    questions: list[GeneratedQuestionSchema] = Field(min_length=1)

    @field_validator("topic", mode="before")
    @classmethod
    def normalize_topic(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("topic must be a string")
        value = _normalize_text(value)
        if not value:
            raise ValueError("topic must not be empty")
        return value

    @model_validator(mode="after")
    def validate_test(self, info: ValidationInfo):
        ctx = info.context or {}

        expected_questions_count = ctx.get("questions_count")
        if expected_questions_count is not None and len(self.questions) != expected_questions_count:
            raise ValueError(f"test must contain exactly {expected_questions_count} questions")

        allowed_subtopics: set[str] | None = ctx.get("allowed_subtopic_names")
        if allowed_subtopics is not None:
            allowed_subtopics = {_normalize_text(x).casefold() for x in allowed_subtopics}
            invalid_subtopics = {
                q.subtopic for q in self.questions
                if _normalize_text(q.subtopic).casefold() not in allowed_subtopics
            }
            if invalid_subtopics:
                raise ValueError(f"questions contain disallowed subtopics: {sorted(invalid_subtopics)}")

        expected_by_subtopic: dict[str, int] | None = ctx.get("questions_by_subtopic")
        if expected_by_subtopic is not None:
            actual = Counter(_normalize_text(q.subtopic).casefold() for q in self.questions)
            expected = Counter({
                _normalize_text(name).casefold(): count
                for name, count in expected_by_subtopic.items()
            })
            if actual != expected:
                raise ValueError("questions count by subtopic does not match expected distribution")

        recent_questions: set[str] | None = ctx.get("recent_questions_normalized")
        if recent_questions is not None:
            for q in self.questions:
                if _normalize_text(q.text).casefold() in recent_questions:
                    raise ValueError("question duplicates a recent question")

        return self


class GeneratedSubtopicSchema(BaseModel):
    name: str

    @model_validator(mode="after")
    def validate_name(self) -> GeneratedSubtopicSchema:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("subtopic name cannot be empty")
        return self


class GeneratedTopicSchema(BaseModel):
    name: str
    subtopics: list[GeneratedSubtopicSchema]

    @model_validator(mode="after")
    def validate_topic(self) -> GeneratedTopicSchema:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("topic name cannot be empty")

        if len(self.subtopics) < 2:
            raise ValueError("each topic must contain at least 2 subtopics")

        subtopic_names = [subtopic.name for subtopic in self.subtopics]
        if len(set(subtopic_names)) != len(subtopic_names):
            raise ValueError("subtopics must be unique inside one topic")

        return self


class GeneratedCourseStructureSchema(BaseModel):
    title: str
    topics: list[GeneratedTopicSchema]

    @model_validator(mode="after")
    def validate_structure(self) -> GeneratedCourseStructureSchema:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("course title cannot be empty")

        if not self.topics:
            raise ValueError("course must contain at least one topic")

        topic_names = [topic.name for topic in self.topics]
        if len(set(topic_names)) != len(topic_names):
            raise ValueError("topics must be unique")

        return self


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
