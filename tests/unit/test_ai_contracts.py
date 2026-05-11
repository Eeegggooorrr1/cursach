import json

import pytest
from pydantic import ValidationError

from ai.schemas import GeneratedCourseStructureSchema, GeneratedTestSchema


def test_generated_test_accepts_multiple_choice_question() -> None:
    payload = {
        "topic": "Python",
        "questions": [
            {
                "subtopic": "Collections",
                "text": "Which are mutable?",
                "question_type": "multiple_choice",
                "options": ["list", "dict", "tuple", "str"],
                "correct_option_indexes": [0, 1],
            }
        ],
    }

    result = GeneratedTestSchema.model_validate_json(
        json.dumps(payload),
        context={
            "questions_count": 1,
            "single_choice_options_range": (2, 6),
            "multiple_choice_options_range": (3, 9),
            "allowed_subtopic_names": {"Collections"},
            "questions_by_subtopic": {"Collections": 1},
            "recent_questions_normalized": set(),
        },
    )

    assert result.questions[0].question_type == "multiple_choice"


def test_generated_test_rejects_partial_multiple_choice_shape() -> None:
    payload = {
        "topic": "Python",
        "questions": [
            {
                "subtopic": "Collections",
                "text": "Which are mutable?",
                "question_type": "multiple_choice",
                "options": ["list", "tuple", "str"],
                "correct_option_indexes": [0],
            }
        ],
    }

    with pytest.raises(ValidationError):
        GeneratedTestSchema.model_validate_json(
            json.dumps(payload),
            context={
                "questions_count": 1,
                "single_choice_options_range": (2, 6),
                "multiple_choice_options_range": (3, 9),
                "allowed_subtopic_names": {"Collections"},
                "questions_by_subtopic": {"Collections": 1},
                "recent_questions_normalized": set(),
            },
        )


def test_generated_test_rejects_recent_question_duplicate() -> None:
    payload = {
        "topic": "Python",
        "questions": [
            {
                "subtopic": "Collections",
                "text": "What is a list?",
                "question_type": "single_choice",
                "options": ["Mutable sequence", "Database"],
                "correct_option_indexes": [0],
            }
        ],
    }

    with pytest.raises(ValidationError):
        GeneratedTestSchema.model_validate_json(
            json.dumps(payload),
            context={
                "questions_count": 1,
                "allowed_subtopic_names": {"Collections"},
                "questions_by_subtopic": {"Collections": 1},
                "recent_questions_normalized": {"what is a list?"},
            },
        )


def test_generated_course_structure_rejects_duplicate_subtopics() -> None:
    with pytest.raises(ValidationError):
        GeneratedCourseStructureSchema.model_validate(
            {
                "title": "Python",
                "topics": [
                    {
                        "name": "Basics",
                        "subtopics": [
                            {"name": "Variables"},
                            {"name": " variables "},
                        ],
                    }
                ],
            }
        )
