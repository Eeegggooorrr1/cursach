from dishka import FromDishka
from dishka.integrations.fastapi import inject

from core.exceptions import ForbiddenError, UserBlockedError
from models.user import RoleEnum
from repositories.user import UserRepository
from schemas.auth import UserFromToken


class RequireRoles:
    def __init__(self, *allowed_roles: RoleEnum):
        self.allowed: set[RoleEnum] = set(allowed_roles)

    @inject
    async def __call__(
        self,
        user: FromDishka[UserFromToken],
        user_repository: FromDishka[UserRepository],
    ) -> UserFromToken:
        actual_user = await user_repository.find_user_by_id(user.id)
        if actual_user is None or actual_user.is_blocked or user.is_blocked:
            raise UserBlockedError()

        if user.role not in self.allowed:
            raise ForbiddenError(
                message="Insufficient role",
                extra={
                    "required_roles": list(self.allowed),
                    "user_role": user.role,
                },
            )
        return user
