from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator, ConfigDict

from models import Question, Test


class CourseCreateSchema(BaseModel):
    title: str
    comment: str | None = None
    topics: list[str] = Field(min_length=1)
    # difficulty: DifficultyEnum = DifficultyEnum.EASY
    # difficulty_mode: DifficultyModeEnum = DifficultyModeEnum.STATIC

    @model_validator(mode="after")
    def validate_topics(self) -> CourseCreateSchema:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("title cannot be empty")

        cleaned_topics = [
            topic.strip() for topic in self.topics if topic.strip()
        ]
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


class PaginationSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int
    limit: int
    offset: int


class CourseListItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    title: str
    comment: str | None
    created_at: datetime


class PaginatedCourseListSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[CourseListItemSchema]
    meta: PaginationSchema


class CourseDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    title: str
    comment: str | None
    created_at: datetime


class CourseHistoryTestItemSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    position: int
    title: str
    status: str
    correct_percentage: float
    error_percentage: float
    started_at: datetime
    finished_at: datetime | None


class PaginatedCourseDetailSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    course: CourseDetailSchema
    tests: list[CourseHistoryTestItemSchema]
    meta: PaginationSchema


class CourseProgressItemSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic_id: int
    topic_name: str
    subtopic_id: int
    subtopic_name: str
    mastery_score: float
    current_difficulty: int
    current_streak: int


class CourseProgressResponseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[CourseProgressItemSchema]


class ReviewOptionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    text: str
    is_correct: bool


class ReviewQuestionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subtopic_id: int
    prompt: str
    options: list[ReviewOptionSchema]

    @classmethod
    def from_orm_question(cls, q: Question):
        return cls(
            id=q.id,
            subtopic_id=q.subtopic_id,
            prompt=q.prompt,
            options=[
                ReviewOptionSchema.model_validate(opt, from_attributes=True)
                for opt in sorted(q.answer_options, key=lambda x: x.position)
            ],
        )


class ReviewTestSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    course_id: int
    position: int
    title: str
    questions: list[ReviewQuestionSchema]

    @classmethod
    def from_orm_test(cls, test: Test):
        return cls(
            id=test.id,
            course_id=test.course_id,
            position=test.position,
            title=test.title,
            questions=[
                ReviewQuestionSchema.from_orm_question(q)
                for q in sorted(test.questions, key=lambda x: x.position)
            ],
        )


class ReviewAttemptSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    question_id: int
    selected_option_id: int | None
    is_correct: bool


class TestReviewResponseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    test: ReviewTestSchema
    attempts: list[ReviewAttemptSchema]
