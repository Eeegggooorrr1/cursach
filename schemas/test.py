from pydantic import Field, model_validator

from schemas.base import OrmSchema, StrictSchema


class TestCreateSchema(StrictSchema):
    topic: str
    questions_count: int = Field(default=10, ge=10, le=24)
    single_choice_options_min: int = Field(default=2, ge=2, le=6)
    single_choice_options_max: int = Field(default=6, ge=2, le=6)
    multiple_choice_options_min: int = Field(default=3, ge=3, le=9)
    multiple_choice_options_max: int = Field(default=9, ge=3, le=9)

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
    question_id: int
    selected_option_ids: list[int] = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_single_choice(cls, value):
        if not isinstance(value, dict):
            return value

        data = dict(value)
        selected_option_id = data.pop("selected_option_id", None)
        if (
            "selected_option_ids" not in data
            and selected_option_id is not None
        ):
            data["selected_option_ids"] = [selected_option_id]
        return data

    @model_validator(mode="after")
    def validate_unique_options(self):
        if len(set(self.selected_option_ids)) != len(self.selected_option_ids):
            raise ValueError("duplicate selected_option_id in submit payload")
        return self


class TestSubmitSchema(StrictSchema):
    answers: list[SubmitAnswerSchema] = Field(min_length=1)

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
