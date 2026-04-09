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


class DoctorNotFoundError(NotFoundError):
    code = "doctor_not_found"
    message = "Doctor not found"


class UserAlreadyExistsError(ConflictError):
    code = "user_already_exists"
    message = "User already exists"


class AppointmentAlreadyExistsError(ConflictError):
    code = "appointment_already_exists"
    message = "Appointment already exists"


class DoctorAlreadyExistsError(ConflictError):
    code = "doctor_already_exists"
    message = "Doctor already exists"


class DoctorSlotBusyError(ConflictError):
    code = "doctor_slot_busy"
    message = "Doctor slot busy"


class VerificationError(BadRequestError):
    code = "verification_failed"
    message = "Verification failed"


class ExternalServiceError(AppError):
    status_code = 502
    code = "external_service_error"
    message = "External service error"


class AppointmentNotFoundError(NotFoundError):
    code = "appointment_not_found"
    message = "Appointment not found"


class AppointmentCannotBeCancelledError(BadRequestError):
    code = "appointment_cannot_be_cancelled"
    message = "Appointment cannot be cancelled"


class AppointmentStatusTransitionError(BadRequestError):
    code = "invalid_appointment_status_transition"
    message = "Invalid appointment status transition"


class TestNotFoundError(Exception):
    pass

class InvalidGeneratedTestError(Exception):
    pass

class InvalidLLMResponseError(Exception):
    pass