import pytest
from pydantic import ValidationError

from schemas.course import CourseCreateSchema
from schemas.test import TestCreateSchema, TestSubmitSchema
from schemas.validation import (
    COURSE_TOPIC_MAX_LENGTH,
    MULTIPLE_CHOICE_OPTIONS_MAX,
)


def test_course_create_schema_normalizes_topics_and_rejects_duplicates() -> None:
    schema = CourseCreateSchema(
        title="  Python  ",
        topics=["  async   io  "],
    )

    assert schema.title == "Python"
    assert schema.topics == ["async io"]

    with pytest.raises(ValidationError):
        CourseCreateSchema(title="Python", topics=["SQL", " sql "])


def test_test_create_schema_rejects_blank_or_too_long_topic() -> None:
    with pytest.raises(ValidationError):
        TestCreateSchema(topic="   ")

    with pytest.raises(ValidationError):
        TestCreateSchema(topic="x" * (COURSE_TOPIC_MAX_LENGTH + 1))


def test_submit_schema_rejects_duplicate_and_invalid_selected_options() -> None:
    with pytest.raises(ValidationError):
        TestSubmitSchema(
            answers=[
                {
                    "question_id": 1,
                    "selected_option_ids": [10, 10],
                }
            ]
        )

    with pytest.raises(ValidationError):
        TestSubmitSchema(
            answers=[
                {
                    "question_id": 1,
                    "selected_option_ids": list(
                        range(1, MULTIPLE_CHOICE_OPTIONS_MAX + 2)
                    ),
                }
            ]
        )
