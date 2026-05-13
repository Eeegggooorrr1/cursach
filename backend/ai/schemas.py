from __future__ import annotations

from collections import Counter
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from pydantic_core.core_schema import ValidationInfo


def normalize_text(value: str) -> str:
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
        value = normalize_text(value)
        if not value:
            raise ValueError("name must not be empty")
        return value


class GeneratedQuestionSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subtopic: str = Field(min_length=1)
    text: str = Field(min_length=1)
    question_type: Literal["single_choice", "multiple_choice"] = "single_choice"
    options: list[str] = Field(min_length=2)
    correct_option_indexes: list[int] = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def normalize_answer_shape(cls, value):
        if not isinstance(value, dict):
            return value

        data = dict(value)
        legacy_correct_index = data.pop("correct_option_index", None)
        if (
            "correct_option_indexes" not in data
            and legacy_correct_index is not None
        ):
            data["correct_option_indexes"] = [legacy_correct_index]

        if "question_type" not in data and isinstance(
            data.get("correct_option_indexes"),
            list,
        ):
            data["question_type"] = (
                "multiple_choice"
                if len(data["correct_option_indexes"]) > 1
                else "single_choice"
            )

        return data

    @field_validator("subtopic", "text", mode="before")
    @classmethod
    def normalize_required_string(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("value must be a string")
        value = normalize_text(value)
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
            item = normalize_text(item)
            if not item:
                raise ValueError("option must not be empty")
            cleaned.append(item)
        return cleaned

    @model_validator(mode="after")
    def validate_question(self, info: ValidationInfo):
        if len(set(self.options)) != len(self.options):
            raise ValueError("duplicated options in one question")

        if len(set(self.correct_option_indexes)) != len(
            self.correct_option_indexes
        ):
            raise ValueError("correct_option_indexes must be unique")

        if any(
            index < 0 or index >= len(self.options)
            for index in self.correct_option_indexes
        ):
            raise ValueError("correct_option_indexes out of range")

        ctx = info.context or {}
        single_range = ctx.get("single_choice_options_range", (2, 6))
        multiple_range = ctx.get("multiple_choice_options_range", (3, 9))

        if self.question_type == "single_choice":
            if len(self.correct_option_indexes) != 1:
                raise ValueError(
                    "single_choice question must have exactly one correct option"
                )
            min_options, max_options = single_range
        else:
            if len(self.correct_option_indexes) < 2:
                raise ValueError(
                    "multiple_choice question must have at least two correct options"
                )
            if len(self.correct_option_indexes) >= len(self.options):
                raise ValueError(
                    "multiple_choice question must have at least one incorrect option"
                )
            min_options, max_options = multiple_range

        if not min_options <= len(self.options) <= max_options:
            raise ValueError(
                f"{self.question_type} question must have between "
                f"{min_options} and {max_options} options"
            )

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
        value = normalize_text(value)
        if not value:
            raise ValueError("topic must not be empty")
        return value

    @model_validator(mode="after")
    def validate_test(self, info: ValidationInfo):
        ctx = info.context or {}

        expected_questions_count = ctx.get("questions_count")
        if (
            expected_questions_count is not None
            and len(self.questions) != expected_questions_count
        ):
            raise ValueError(
                f"test must contain exactly {expected_questions_count} questions"
            )

        allowed_subtopics: set[str] | None = ctx.get("allowed_subtopic_names")
        if allowed_subtopics is not None:
            allowed_subtopics = {
                normalize_text(x).casefold() for x in allowed_subtopics
            }
            invalid_subtopics = {
                q.subtopic
                for q in self.questions
                if normalize_text(q.subtopic).casefold()
                not in allowed_subtopics
            }
            if invalid_subtopics:
                raise ValueError(
                    f"questions contain disallowed subtopics: {sorted(invalid_subtopics)}"
                )

        expected_by_subtopic: dict[str, int] | None = ctx.get(
            "questions_by_subtopic"
        )
        if expected_by_subtopic is not None:
            actual = Counter(
                normalize_text(q.subtopic).casefold()
                for q in self.questions
            )
            expected = Counter(
                {
                    normalize_text(name).casefold(): count
                    for name, count in expected_by_subtopic.items()
                }
            )
            if actual != expected:
                raise ValueError(
                    "questions count by subtopic does not match expected distribution"
                )

        recent_questions: set[str] | None = ctx.get(
            "recent_questions_normalized"
        )
        if recent_questions is not None:
            for q in self.questions:
                if normalize_text(q.text).casefold() in recent_questions:
                    raise ValueError("question duplicates a recent question")

        return self


class GeneratedSubtopicSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str

    @model_validator(mode="after")
    def validate_name(self) -> GeneratedSubtopicSchema:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("subtopic name cannot be empty")
        return self


class GeneratedTopicSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    subtopics: list[GeneratedSubtopicSchema]

    @model_validator(mode="after")
    def validate_topic(self) -> GeneratedTopicSchema:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("topic name cannot be empty")

        if len(self.subtopics) < 2:
            raise ValueError("each topic must contain at least 2 subtopics")

        subtopic_names = [
            normalize_text(subtopic.name).casefold()
            for subtopic in self.subtopics
        ]
        if len(set(subtopic_names)) != len(subtopic_names):
            raise ValueError("subtopics must be unique inside one topic")

        return self


class GeneratedCourseStructureSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    topics: list[GeneratedTopicSchema]

    @model_validator(mode="after")
    def validate_structure(self) -> GeneratedCourseStructureSchema:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("course title cannot be empty")

        if not self.topics:
            raise ValueError("course must contain at least one topic")

        topic_names = [
            normalize_text(topic.name).casefold() for topic in self.topics
        ]
        if len(set(topic_names)) != len(topic_names):
            raise ValueError("topics must be unique")

        return self
