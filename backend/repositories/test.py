from dataclasses import dataclass

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.dto import PreparedQuestionData
from models.test import AnswerOption, Question, Test


@dataclass
class TestRepository:
    session: AsyncSession

    async def get_next_position(self, course_id: int, user_id: int) -> int:
        stmt = select(func.coalesce(func.max(Test.position), 0) + 1).where(
            Test.course_id == course_id,
            Test.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create_test(
        self,
        course_id: int,
        user_id: int,
        position: int,
        title: str,
        questions: list[PreparedQuestionData],
    ) -> Test:
        test = Test(
            course_id=course_id,
            user_id=user_id,
            title=title,
            position=position,
        )
        self.session.add(test)
        await self.session.flush()

        for question_position, question_data in enumerate(questions):
            question = Question(
                test_id=test.id,
                subtopic_id=question_data.subtopic_id,
                prompt=question_data.prompt,
                is_multiple_choice=question_data.is_multiple_choice,
                position=question_position,
            )

            correct_option_indexes = set(question_data.correct_option_indexes)
            question.answer_options = [
                AnswerOption(
                    position=option_position,
                    text=option_text,
                    is_correct=(
                        option_position in correct_option_indexes
                    ),
                )
                for option_position, option_text in enumerate(
                    question_data.options
                )
            ]

            self.session.add(question)

        await self.session.flush()
        return test

    async def get_test_with_details(self, test_id: int) -> Test | None:
        stmt = (
            select(Test)
            .where(Test.id == test_id)
            .options(
                selectinload(Test.questions).selectinload(
                    Question.answer_options
                ),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
