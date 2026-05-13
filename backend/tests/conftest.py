from __future__ import annotations

import json
from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone

import httpx
import pytest
import pytest_asyncio
from jose import jwt
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
)

from core.auth.tokens import ACCESS_TOKEN_COOKIE
from core.config import Settings
from core.db import create_database_engine, create_database_sessionmaker
from models.course import Course, Subtopic, Topic
from models.progress import SubtopicProgress, TestProgress
from models.test import AnswerOption, Question, Test
from models.user import Role, RoleEnum, User, UserCourse
from tests.app import create_test_app
from tests.db.bootstrap_current_models import downgrade, upgrade
from tests.fakes import FakeLLMClient
from tests.settings import TestSettings, create_test_settings


@pytest.fixture(scope="session")
def test_settings() -> TestSettings:
    return create_test_settings()


@pytest_asyncio.fixture
async def db_engine(test_settings: Settings) -> AsyncIterator[AsyncEngine]:
    engine = create_database_engine(test_settings)
    try:
        await upgrade(engine)
    except (OSError, OperationalError) as exc:
        await engine.dispose()
        pytest.skip(
            f"Test database is unavailable at {test_settings.database_url}: {exc}"
        )

    maker = create_database_sessionmaker(engine)
    async with maker() as session:
        await seed_roles(session)
        await session.commit()

    try:
        yield engine
    finally:
        await downgrade(engine)
        await engine.dispose()


@pytest_asyncio.fixture
async def db_session(
    db_engine: AsyncEngine,
) -> AsyncIterator[AsyncSession]:
    maker = create_database_sessionmaker(db_engine)
    async with maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def fake_llm_client() -> FakeLLMClient:
    return FakeLLMClient()


@pytest_asyncio.fixture
async def api_client(
    test_settings: Settings,
    db_engine: AsyncEngine,
    fake_llm_client: FakeLLMClient,
) -> AsyncIterator[httpx.AsyncClient]:
    app = create_test_app(
        settings=test_settings,
        engine=db_engine,
        llm_client=fake_llm_client,
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        yield client
    await app.state.dishka_container.close()


def auth_cookies_for_user(
    user: User,
    settings: Settings,
) -> dict[str, str]:
    token = jwt.encode(
        {
            "sub": str(user.id),
            "role": user.role.name,
            "username": user.username,
            "is_blocked": user.is_blocked,
            "name": "access",
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.ACCESS_EXPIRES_MINUTES),
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return {ACCESS_TOKEN_COOKIE: token}


def use_auth_cookies(
    client: httpx.AsyncClient,
    cookies: dict[str, str],
) -> None:
    client.cookies.clear()
    client.cookies.update(cookies)


def generated_course_response(
    *,
    title: str,
    topics: list[str],
    subtopics_count: int,
) -> str:
    return json.dumps(
        {
            "title": title,
            "topics": [
                {
                    "name": topic,
                    "subtopics": [
                        {"name": f"{topic} subtopic {index + 1}"}
                        for index in range(subtopics_count)
                    ],
                }
                for topic in topics
            ],
        }
    )


def generated_test_response(
    *,
    topic: str,
    subtopic_question_counts: dict[str, int],
) -> str:
    questions = []
    question_no = 1
    for subtopic_name, count in subtopic_question_counts.items():
        for _ in range(count):
            is_multiple = question_no % 3 == 0
            if is_multiple:
                questions.append(
                    {
                        "subtopic": subtopic_name,
                        "text": f"Question {question_no}",
                        "question_type": "multiple_choice",
                        "options": ["A", "B", "C", "D"],
                        "correct_option_indexes": [0, 2],
                    }
                )
            else:
                questions.append(
                    {
                        "subtopic": subtopic_name,
                        "text": f"Question {question_no}",
                        "question_type": "single_choice",
                        "options": ["A", "B", "C"],
                        "correct_option_indexes": [1],
                    }
                )
            question_no += 1
    return json.dumps({"topic": topic, "questions": questions})


async def seed_roles(session: AsyncSession) -> None:
    session.add_all(
        [
            Role(id=1, name=RoleEnum.USER.value),
            Role(id=2, name=RoleEnum.ADMIN.value),
        ]
    )
    await session.flush()


async def create_user(
    session: AsyncSession,
    *,
    email: str = "user@example.com",
    username: str = "user",
    role_id: int = 1,
    is_blocked: bool = False,
) -> User:
    user = User(
        email=email,
        username=username,
        password="hashed",
        role_id=role_id,
        is_blocked=is_blocked,
    )
    session.add(user)
    await session.flush()
    await session.refresh(user, attribute_names=["role"])
    return user


async def create_course(
    session: AsyncSession,
    *,
    creator: User,
    title: str = "Course",
    is_public: bool = False,
    is_public_allowed: bool = True,
) -> Course:
    course = Course(
        creator_id=creator.id,
        title=title,
        comment="Comment",
        prompt="Prompt",
        is_public=is_public,
        is_public_allowed=is_public_allowed,
    )
    session.add(course)
    await session.flush()
    session.add(UserCourse(user_id=creator.id, course_id=course.id))
    await session.flush()
    return course


async def add_course_structure(
    session: AsyncSession,
    course: Course,
) -> Subtopic:
    topic = Topic(course_id=course.id, name="Topic")
    topic.subtopics = [Subtopic(name="Subtopic")]
    session.add(topic)
    await session.flush()
    return topic.subtopics[0]


async def create_test_with_questions(
    session: AsyncSession,
    *,
    course: Course,
    user: User,
    subtopic: Subtopic,
    multiple_choice: bool = True,
) -> tuple[Test, Question, list[AnswerOption], TestProgress]:
    test = Test(
        course_id=course.id,
        user_id=user.id,
        title="Test",
        position=1,
    )
    question = Question(
        test=test,
        subtopic_id=subtopic.id,
        prompt="Question",
        is_multiple_choice=multiple_choice,
        position=0,
    )
    question.answer_options = [
        AnswerOption(text="A", is_correct=True, position=0),
        AnswerOption(text="B", is_correct=True, position=1),
        AnswerOption(text="C", is_correct=False, position=2),
    ]
    session.add(test)
    await session.flush()
    progress = TestProgress(
        user_id=user.id,
        test_id=test.id,
        started_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    session.add(progress)
    await session.flush()
    return test, question, question.answer_options, progress


async def create_subtopic_progress(
    session: AsyncSession,
    *,
    user: User,
    subtopic: Subtopic,
    mastery_score: float,
    current_difficulty: int,
    current_streak: int = 0,
) -> SubtopicProgress:
    progress = SubtopicProgress(
        user_id=user.id,
        subtopic_id=subtopic.id,
        mastery_score=mastery_score,
        current_difficulty=current_difficulty,
        current_streak=current_streak,
    )
    session.add(progress)
    await session.flush()
    return progress
