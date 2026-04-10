from pydantic import BaseModel, Field


class TestCreateSchema(BaseModel):
    topic: str
    questions_count: int = Field(ge=1, le=20)
    options_count: int = Field(ge=2, le=8)


class TestOptionReadSchema(BaseModel):
    id: int
    text: str
    is_correct: bool


class TestQuestionReadSchema(BaseModel):
    id: int
    position: int
    text: str
    options: list[TestOptionReadSchema]


class TestReadSchema(BaseModel):
    id: int
    user_id: int
    topic: str
    questions_count: int
    options_count: int
    status: str
    questions: list[TestQuestionReadSchema]
