from datetime import datetime, timedelta, UTC
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from app.db.Config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return jwt.encode({"sub": subject, "exp": expire, "type": "access"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_email_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(hours=settings.EMAIL_TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": subject, "exp": expire, "type": "email_confirm"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str, expected_type: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        if payload.get("type") != expected_type:
            return None

        return payload.get("sub")
    except InvalidTokenError:
        return None