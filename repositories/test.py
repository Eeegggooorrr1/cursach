from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ai.contracts import GeneratedTestSchema
from core.exceptions import TestNotFoundError
from models.test import AnswerOption, Question, Test


class TestRepository:
    model = Test

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_test(
        self,
        topic: str,
        questions_count: int,
        options_count: int,
        user_id: int,
        generated: GeneratedTestSchema,
    ) -> Test:
        test = Test(
            topic=topic,
            questions_count=questions_count,
            options_count=options_count,
            user_id=user_id,
        )
        self.session.add(test)
        await self.session.flush()

        for question_position, question_data in enumerate(generated.questions):
            question = Question(
                test_id=test.id,
                position=question_position,
                text=question_data.text.strip(),
            )

            for option_position, option_text in enumerate(question_data.options):
                question.options.append(
                    AnswerOption(
                        position=option_position,
                        text=option_text.strip(),
                        is_correct=(
                            option_position == question_data.correct_option_index
                        ),
                    )
                )
            self.session.add(question)

        await self.session.flush()
        return test

    async def get_test_with_details(self, test_id: int) -> Test | None:
        stmt = (
            select(Test)
            .where(Test.id == test_id)
            .options(
                selectinload(Test.questions).selectinload(Question.options),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()