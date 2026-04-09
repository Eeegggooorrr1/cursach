from dataclasses import dataclass
import json

from pydantic import EmailStr

from core.exceptions import ExternalServiceError, UserNotFoundError, \
    InvalidLoginOrPasswordError, UserAlreadyExistsError
from models.user import User, RoleEnum
from repositories.user import UserRepository
from schemas.user import (
    UserCreateSchema,
)
from services.security import SecurityService


@dataclass
class AuthService:
    user_repository: UserRepository
    security_service: SecurityService

    async def login(self, email: EmailStr, password: str) -> tuple[
        str, str]:
        user = await self.user_repository.find_user_by_email(
            email=email)
        if not user:
            raise UserNotFoundError()

        if not self.security_service.verify_password(password, user.password):
            raise InvalidLoginOrPasswordError()

        access_token, refresh_token = await self.security_service.issue_token_pair(user)

        return access_token, refresh_token

    async def register(self, email: EmailStr, password: str, username: str) -> tuple[str, str]:
        user = await self.user_repository.find_user_by_email(
            email=email)
        if user:
            raise UserAlreadyExistsError()

        hashed_password = self.security_service.get_password_hash(password)

        user = await self.user_repository.create_user(UserCreateSchema(
            email=email,
            password=hashed_password,
            username=username
        ))

        access_token, refresh_token = await self.security_service.issue_token_pair(
            user)

        return access_token, refresh_token

