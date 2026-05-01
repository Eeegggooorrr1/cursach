from pydantic import Field, model_validator

from schemas.base import OrmSchema, StrictSchema


class TestCreateSchema(StrictSchema):
    topic: str
    questions_count: int = Field(ge=1, le=20)
    options_count: int = Field(ge=2, le=8)


class TestOptionReadSchema(OrmSchema):
    id: int
    text: str


class TestQuestionReadSchema(OrmSchema):
    id: int
    subtopic_id: int
    prompt: str
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
    selected_option_id: int


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
