from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets
import string

from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext

from core.config import Settings
from core.exceptions import (
    TokenError,
    TokenExpiredError,
    TokenNotFoundError,
    TokenRevokedError,
    UserNotFoundError,
)
from models.user import User
from repositories.refresh_token import RefreshTokenRepository
from repositories.user import UserRepository


@dataclass(slots=True)
class SecurityService:
    user_repository: UserRepository
    refresh_repository: RefreshTokenRepository
    settings: Settings
    pwd_context: CryptContext

    @staticmethod
    def _build_token_payload(user: User) -> dict:
        return {
            "sub": str(user.id),
            "role": user.role.name,
            "username": user.username,
        }

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def _get_token_hash(self, token: str) -> str:
        return hmac.new(
            key=self.settings.SECRET_KEY.encode(),
            msg=token.encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()

    def _create_token(
        self,
        data: dict,
        name: str,
        exp: timedelta | None = None,
    ) -> str:
        to_encode = data.copy()

        if exp:
            expire = datetime.now(timezone.utc) + exp
            to_encode.update({"exp": expire})

        to_encode.update({"name": name})

        return jwt.encode(
            to_encode,
            self.settings.SECRET_KEY,
            algorithm=self.settings.ALGORITHM,
        )

    def issue_access_token(self, user: User) -> str:
        return self._create_token(
            data=self._build_token_payload(user),
            name="access",
            exp=timedelta(minutes=self.settings.ACCESS_EXPIRES_MINUTES),
        )

    @staticmethod
    def _create_random_token(length: int = 64) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def create_refresh_token(self, length: int = 64) -> str:
        return self._create_random_token(length=length)

    def decode_token(self, token: str, expected_name: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                self.settings.SECRET_KEY,
                algorithms=[self.settings.ALGORITHM],
            )
        except ExpiredSignatureError as exc:
            raise TokenExpiredError() from exc
        except JWTError as exc:
            raise TokenError("Token decode failed") from exc

        user_id = payload.get("sub")
        if not user_id:
            raise TokenError("Token missing sub")

        token_name = payload.get("name")
        if token_name != expected_name:
            raise TokenError("Token type mismatch")

        return payload

    async def issue_token_pair(self, user: User) -> tuple[str, str]:
        access_token = self.issue_access_token(user)
        refresh_token = self.create_refresh_token()
        refresh_token_hashed = self._get_token_hash(refresh_token)

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=self.settings.REFRESH_EXPIRES_DAYS
        )

        await self.refresh_repository.create_and_revoke_all_for_user(
            new_token=refresh_token_hashed,
            user_id=user.id,
            expires_at=expires_at,
        )

        return access_token, refresh_token

    async def refresh_tokens(self, token: str) -> tuple[str, str]:
        token_hash = self._get_token_hash(token)

        token_record = await self.refresh_repository.get_by_token(token_hash)
        if not token_record:
            raise TokenNotFoundError()

        if token_record.revoked_at is not None:
            await self.refresh_repository.revoke_all_for_user(token_record.user_id)
            raise TokenRevokedError()

        if token_record.expires_at < datetime.now(timezone.utc):
            raise TokenExpiredError()

        user = await self.user_repository.find_user_by_id(token_record.user_id)
        if not user:
            raise UserNotFoundError()

        access_token = self.issue_access_token(user)
        new_refresh_token = self.create_refresh_token()

        await self.refresh_repository.rotate_token(
            old_token=token_hash,
            new_token=self._get_token_hash(new_refresh_token),
            user_id=user.id,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=self.settings.REFRESH_EXPIRES_DAYS),
        )

        return access_token, new_refresh_token
