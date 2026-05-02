from dataclasses import dataclass

from core.exceptions import UserNotFoundError
from repositories.user import UserRepository
from schemas.user import UserProfileSchema, UserUpdateSchema


@dataclass
class UserService:
    user_repository: UserRepository

    async def get_profile(self, user_id: int) -> UserProfileSchema:
        user = await self.user_repository.find_user_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundError()

        return UserProfileSchema(
            id=user.id,
            email=user.email,
            username=user.username,
            profile_description=user.profile_description,
            role=user.role.name,
        )

    async def update_profile(
        self,
        user_id: int,
        payload: UserUpdateSchema,
    ) -> UserProfileSchema:
        user = await self.user_repository.update_user(
            user_id=user_id,
            user_data=payload,
        )
        if user is None:
            raise UserNotFoundError()

        return UserProfileSchema(
            id=user.id,
            email=user.email,
            username=user.username,
            profile_description=user.profile_description,
            role=user.role.name,
        )
