from dataclasses import dataclass

from pydantic import ValidationError

from ai.contracts import GeneratedTestSchema, LLMClient
from ai.prompts.test_generation.factory import TestGenerationPromptFactory
from core.exceptions import (
    InvalidGeneratedTestError,
    InvalidLLMResponseError,
    TestNotFoundError,
)
from repositories.test import TestRepository


@dataclass
class TestService:
    test_repository: TestRepository
    llm_client: LLMClient
    prompt_factory: TestGenerationPromptFactory

    async def create_test(
        self,
        topic: str,
        questions_count: int,
        options_count: int,
        user_id: int,
    ):

        draft = await self.test_repository.create_draft_test(
            topic=topic,
            questions_count=questions_count,
            options_count=options_count,
            user_id=user_id,
        )

        try:
            prompt = self.prompt_factory.build(
                topic=topic,
                questions_count=questions_count,
                options_count=options_count,
            )

            try:
                raw_answer = await self.llm_client.complete(
                    system=prompt.system,
                    user=prompt.user,
                    temperature=0.0,
                )
            except Exception as exc:
                raise InvalidLLMResponseError(
                    message="LLM request failed"
                ) from exc

            try:
                generated = GeneratedTestSchema.model_validate_json(
                    raw_answer)
            except ValidationError as exc:
                raise InvalidLLMResponseError(
                    message="LLM returned invalid JSON/schema"
                ) from exc

            self._validate_generated_test(
                generated=generated,
                expected_questions=questions_count,
                expected_options=options_count,
            )

            test = await self.test_repository.save_generated_test(
                test_id=draft.id,
                generated=generated,
            )

            full_test = await self.test_repository.get_test_with_details(
                test.id)
            if not full_test:
                raise TestNotFoundError()

            return full_test

        except Exception:
            raise

    @staticmethod
    def _validate_generated_test(
        generated: GeneratedTestSchema,
        expected_questions: int,
        expected_options: int,
    ) -> None:
        if len(generated.questions) != expected_questions:
            raise InvalidGeneratedTestError(
                message="LLM returned wrong number of questions",
                extra={
                    "expected_questions": expected_questions,
                    "actual_questions": len(generated.questions),
                },
            )

        for index, question in enumerate(generated.questions):
            if not question.text.strip():
                raise InvalidGeneratedTestError(
                    message="Empty question text from LLM",
                    extra={"question_index": index},
                )

            if len(question.options) != expected_options:
                raise InvalidGeneratedTestError(
                    message="LLM returned wrong number of options",
                    extra={
                        "question_index": index,
                        "expected_options": expected_options,
                        "actual_options": len(question.options),
                    },
                )

            if not 0 <= question.correct_option_index < expected_options:
                raise InvalidGeneratedTestError(
                    message="correct_option_index out of range",
                    extra={
                        "question_index": index,
                        "correct_option_index": question.correct_option_index,
                        "expected_options": expected_options,
                    },
                )

            normalized = [option.strip() for option in question.options]

            if len(set(normalized)) != len(normalized):
                raise InvalidGeneratedTestError(
                    message="Duplicated options in one question",
                    extra={"question_index": index},
                )

            if not normalized[question.correct_option_index]:
                raise InvalidGeneratedTestError(
                    message="Correct option is empty",
                    extra={"question_index": index},
                )
