from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

from pydantic import BaseModel, model_validator


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


class GeneratedTestQuestionSchema(BaseModel):
    text: str
    options: list[str]
    correct_option_index: int


class GeneratedTestSchema(BaseModel):
    topic: str
    questions: list[GeneratedTestQuestionSchema]


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
