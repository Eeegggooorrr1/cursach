from pydantic import BaseModel, Field, ConfigDict

from models import Question


class TestCreateSchema(BaseModel):
    topic: str
    questions_count: int = Field(ge=1, le=20)
    options_count: int = Field(ge=2, le=8)


class TestOptionReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
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