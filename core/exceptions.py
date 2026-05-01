from typing import Any


class AppError(Exception):
    status_code: int = 500
    code: str = "internal_error"
    message: str = "Internal server error"

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        status_code: int | None = None,
        extra: Any | None = None,
    ):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        self.extra = extra
        super().__init__(self.message)


class BadRequestError(AppError):
    status_code = 400
    code = "bad_request"
    message = "Bad request"


class UnauthorizedError(AppError):
    status_code = 401
    code = "unauthorized"
    message = "Authentication failed"


class ForbiddenError(AppError):
    status_code = 403
    code = "forbidden"
    message = "Forbidden"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"
    message = "Resource not found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"
    message = "Conflict"

class ExternalServiceError(AppError):
    status_code = 502
    code = "external_service_error"
    message = "External service error"


class TokenError(UnauthorizedError):
    code = "token_error"
    message = "Token is invalid"


class TokenExpiredError(TokenError):
    code = "token_expired"
    message = "Token has expired"


class TokenRevokedError(TokenError):
    code = "token_revoked"
    message = "Token has been revoked"


class TokenNotFoundError(TokenError):
    code = "token_not_found"
    message = "Token not found"


class AuthenticationError(UnauthorizedError):
    code = "authentication_failed"
    message = "Authentication failed"


class InvalidCredentialsError(AuthenticationError):
    code = "invalid_credentials"
    message = "Invalid credentials"


class InvalidLoginOrPasswordError(AuthenticationError):
    code = "invalid_login_or_password"
    message = "Invalid login or password"


class UserNotFoundError(NotFoundError):
    code = "user_not_found"
    message = "User not found"


class CourseNotFoundError(NotFoundError):
    code = "course_not_found"
    message = "Course not found"


class UserAlreadyExistsError(ConflictError):
    code = "user_already_exists"
    message = "User already exists"



class TestNotFoundError(NotFoundError):
    code = "test_not_found"
    message = "Test not found"


class InvalidGeneratedTestError(ExternalServiceError):
    code = "invalid_generated_test"
    message = "Generated test is invalid"


class InvalidLLMResponseError(ExternalServiceError):
    code = "invalid_llm_response"
    message = "LLM response is invalid"


class InvalidCourseStructureError(ExternalServiceError):
    code = "invalid_course_structure"
    message = "Invalid course structure"


class TestAlreadySubmittedError(ConflictError):
    code = "test_already_submitted"
    message = "Test already submitted"


class InvalidTestSubmissionError(BadRequestError):
    code = "invalid_test_submission"
    message = "Invalid test submission"

class TestReviewNotAvailableError(ConflictError):
    code = "test_review_not_available"
    message = "Test review_not_available"
