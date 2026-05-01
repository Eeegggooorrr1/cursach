from __future__ import annotations

from datetime import datetime

from pydantic import Field, model_validator

from core.enums import Difficulty
from models import Question, Test
from schemas.base import OrmSchema, StrictSchema


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


class CourseCreateSchema(StrictSchema):
    title: str
    comment: str | None = None
    prompt: str | None = None
    topics: list[str] = Field(min_length=1)
    initial_difficulty: Difficulty = Difficulty.EASY
    is_public: bool = False

    @model_validator(mode="after")
    def validate_course(self) -> CourseCreateSchema:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("title cannot be empty")

        self.comment = _clean_optional_text(self.comment)
        self.prompt = _clean_optional_text(self.prompt)

        cleaned_topics = [
            " ".join(topic.strip().split())
            for topic in self.topics
            if topic.strip()
        ]
        if not cleaned_topics:
            raise ValueError("topics list cannot be empty")

        normalized_topics = [topic.casefold() for topic in cleaned_topics]
        if len(set(normalized_topics)) != len(normalized_topics):
            raise ValueError("topics must be unique")

        self.topics = cleaned_topics
        return self


class CourseEnrollSchema(StrictSchema):
    initial_difficulty: Difficulty = Difficulty.EASY


class CourseVisibilityUpdateSchema(StrictSchema):
    is_public: bool


class CourseEnrollmentResponseSchema(StrictSchema):
    course_id: int
    user_id: int
    enrolled: bool


class SubtopicReadSchema(OrmSchema):
    id: int
    name: str


class TopicReadSchema(OrmSchema):
    id: int
    name: str
    subtopics: list[SubtopicReadSchema]


class CourseReadSchema(OrmSchema):
    id: int
    creator_id: int
    title: str
    comment: str | None
    prompt: str | None
    is_public: bool
    created_at: datetime
    topics: list[TopicReadSchema]


class PaginationSchema(StrictSchema):
    total: int
    limit: int
    offset: int


class CourseListItemSchema(OrmSchema):
    id: int
    creator_id: int
    title: str
    comment: str | None
    is_public: bool
    created_at: datetime


class PaginatedCourseListSchema(StrictSchema):
    items: list[CourseListItemSchema]
    meta: PaginationSchema


class PublicCourseDetailSchema(OrmSchema):
    id: int
    creator_id: int
    title: str
    comment: str | None
    is_public: bool
    created_at: datetime
    topics: list[TopicReadSchema]


class CourseDetailSchema(OrmSchema):
    id: int
    creator_id: int
    title: str
    comment: str | None
    prompt: str | None
    is_public: bool
    created_at: datetime


class CourseHistoryTestItemSchema(StrictSchema):
    id: int
    position: int
    title: str
    status: str
    correct_percentage: float
    error_percentage: float
    started_at: datetime
    finished_at: datetime | None


class PaginatedCourseDetailSchema(StrictSchema):
    course: CourseDetailSchema
    tests: list[CourseHistoryTestItemSchema]
    meta: PaginationSchema


class CourseProgressItemSchema(StrictSchema):
    topic_id: int
    topic_name: str
    subtopic_id: int
    subtopic_name: str
    mastery_score: float
    current_difficulty: int
    current_streak: int


class CourseProgressResponseSchema(StrictSchema):
    items: list[CourseProgressItemSchema]


class ReviewOptionSchema(OrmSchema):
    id: int
    text: str
    is_correct: bool


class ReviewQuestionSchema(OrmSchema):
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


class ReviewTestSchema(StrictSchema):
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


class ReviewAttemptSchema(OrmSchema):
    question_id: int
    selected_option_id: int | None
    is_correct: bool


class TestReviewResponseSchema(StrictSchema):
    test: ReviewTestSchema
    attempts: list[ReviewAttemptSchema]
