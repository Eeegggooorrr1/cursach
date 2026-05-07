from passlib.context import CryptContext


def create_password_context() -> CryptContext:
    return CryptContext(schemes=["bcrypt"], deprecated="auto")
