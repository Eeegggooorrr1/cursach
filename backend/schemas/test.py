from typing import Annotated

from pydantic import Field, PositiveInt, StringConstraints, model_validator

from schemas.base import OrmSchema, StrictSchema
from schemas.validation import (
    COURSE_TOPIC_MAX_LENGTH,
    MULTIPLE_CHOICE_OPTIONS_MAX,
    MULTIPLE_CHOICE_OPTIONS_MIN,
    SINGLE_CHOICE_OPTIONS_MAX,
    SINGLE_CHOICE_OPTIONS_MIN,
    TEST_QUESTIONS_MAX_COUNT,
    TEST_QUESTIONS_MIN_COUNT,
)


class TestCreateSchema(StrictSchema):
    topic: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            max_length=COURSE_TOPIC_MAX_LENGTH,
        ),
    ]
    questions_count: int = Field(
        default=TEST_QUESTIONS_MIN_COUNT,
        ge=TEST_QUESTIONS_MIN_COUNT,
        le=TEST_QUESTIONS_MAX_COUNT,
    )
    single_choice_options_min: int = Field(
        default=SINGLE_CHOICE_OPTIONS_MIN,
        ge=SINGLE_CHOICE_OPTIONS_MIN,
        le=SINGLE_CHOICE_OPTIONS_MAX,
    )
    single_choice_options_max: int = Field(
        default=SINGLE_CHOICE_OPTIONS_MAX,
        ge=SINGLE_CHOICE_OPTIONS_MIN,
        le=SINGLE_CHOICE_OPTIONS_MAX,
    )
    multiple_choice_options_min: int = Field(
        default=MULTIPLE_CHOICE_OPTIONS_MIN,
        ge=MULTIPLE_CHOICE_OPTIONS_MIN,
        le=MULTIPLE_CHOICE_OPTIONS_MAX,
    )
    multiple_choice_options_max: int = Field(
        default=MULTIPLE_CHOICE_OPTIONS_MAX,
        ge=MULTIPLE_CHOICE_OPTIONS_MIN,
        le=MULTIPLE_CHOICE_OPTIONS_MAX,
    )

    @model_validator(mode="after")
    def validate_ranges(self):
        if self.single_choice_options_min > self.single_choice_options_max:
            raise ValueError("single choice options range is invalid")
        if self.multiple_choice_options_min > self.multiple_choice_options_max:
            raise ValueError("multiple choice options range is invalid")
        return self


class TestOptionReadSchema(OrmSchema):
    id: int
    text: str


class TestQuestionReadSchema(OrmSchema):
    id: int
    subtopic_id: int
    prompt: str
    is_multiple_choice: bool
    options: list[TestOptionReadSchema] = Field(
        validation_alias="answer_options",
    )


class TestReadSchema(OrmSchema):
    id: int
    course_id: int
    user_id: int
    position: int
    title: str
    questions: list[TestQuestionReadSchema]


class SubmitAnswerSchema(StrictSchema):
    question_id: PositiveInt
    selected_option_ids: list[PositiveInt] = Field(
        min_length=1,
        max_length=MULTIPLE_CHOICE_OPTIONS_MAX,
    )

    @model_validator(mode="after")
    def validate_unique_options(self):
        if len(set(self.selected_option_ids)) != len(self.selected_option_ids):
            raise ValueError("duplicate selected option in submit payload")
        return self


class TestSubmitSchema(StrictSchema):
    answers: list[SubmitAnswerSchema] = Field(
        min_length=1,
        max_length=TEST_QUESTIONS_MAX_COUNT,
    )

    @model_validator(mode="after")
    def validate_unique_questions(self):
        question_ids = [item.question_id for item in self.answers]
        if len(set(question_ids)) != len(question_ids):
            raise ValueError("duplicate question_id in submit payload")
        return self


class TestSubmitResponseSchema(StrictSchema):
    test_progress_id: int
    test_id: int
    status: str
    correct_percentage: float
