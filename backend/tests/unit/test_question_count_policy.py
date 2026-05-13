from core.enums import Difficulty
import services.test as test_service
from tests.factories import make_subtopic, make_subtopic_progress


def test_policy_keeps_question_count_between_bounds() -> None:
    subtopics = [make_subtopic(index) for index in range(1, 31)]

    plan = test_service.TestQuestionCountPolicy().build_subtopic_plan(
        subtopics=subtopics,
        progress_by_subtopic_id={},
        test_no=1,
    )

    assert len(plan) == 24
    assert 10 <= sum(item["questions_count"] for item in plan) <= 24


def test_policy_rotates_large_course_subtopic_window() -> None:
    subtopics = [make_subtopic(index) for index in range(1, 31)]
    policy = test_service.TestQuestionCountPolicy()

    first_plan = policy.build_subtopic_plan(
        subtopics=subtopics,
        progress_by_subtopic_id={},
        test_no=1,
    )
    second_plan = policy.build_subtopic_plan(
        subtopics=subtopics,
        progress_by_subtopic_id={},
        test_no=2,
    )

    assert first_plan[0]["name"] == "Subtopic 1"
    assert second_plan[0]["name"] == "Subtopic 25"


def test_policy_assigns_extra_questions_to_harder_subtopics_first() -> None:
    subtopics = [make_subtopic(index) for index in range(1, 4)]
    progress = {
        1: make_subtopic_progress(
            1,
            mastery_score=0.0,
            current_difficulty=Difficulty.EASY,
        ),
        2: make_subtopic_progress(
            2,
            mastery_score=0.0,
            current_difficulty=Difficulty.HARD,
        ),
        3: make_subtopic_progress(
            3,
            mastery_score=0.0,
            current_difficulty=Difficulty.MEDIUM,
        ),
    }

    plan = test_service.TestQuestionCountPolicy().build_subtopic_plan(
        subtopics=subtopics,
        progress_by_subtopic_id=progress,
        test_no=1,
    )

    questions_by_name = {
        item["name"]: item["questions_count"] for item in plan
    }
    assert questions_by_name["Subtopic 2"] >= questions_by_name["Subtopic 3"]
    assert questions_by_name["Subtopic 3"] >= questions_by_name["Subtopic 1"]
    assert sum(questions_by_name.values()) == 10
