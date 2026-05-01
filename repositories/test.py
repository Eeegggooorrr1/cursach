from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.dto import PreparedQuestionData
from models.test import AnswerOption, Question, Test


class TestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

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
                position=question_position,
            )

            question.answer_options = [
                AnswerOption(
                    position=option_position,
                    text=option_text,
                    is_correct=(
                        option_position == question_data.correct_option_index
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
