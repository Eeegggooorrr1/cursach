from __future__ import annotations
from pydantic import BaseModel, Field, model_validator


class CourseCreateSchema(BaseModel):
    title: str
    comment: str | None = None
    topics: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_topics(self) -> CourseCreateSchema:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("title cannot be empty")

        cleaned_topics = [topic.strip() for topic in self.topics if topic.strip()]
        if not cleaned_topics:
            raise ValueError("topics list cannot be empty")

        if len(set(cleaned_topics)) != len(cleaned_topics):
            raise ValueError("topics must be unique")

        self.topics = cleaned_topics
        return self



class SubtopicReadSchema(BaseModel):
    id: int
    name: str


class TopicReadSchema(BaseModel):
    id: int
    name: str
    subtopics: list[SubtopicReadSchema]


class CourseReadSchema(BaseModel):
    id: int
    title: str
    comment: str | None
    topics: list[TopicReadSchema]