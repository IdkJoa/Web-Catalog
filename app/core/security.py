from datetime import datetime, timedelta, UTC

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic.v1 import EmailStr

from app.core.dependencies import oauth2_scheme
from app.db.Config import settings
from app.services.auth import register_user
from app.db.db_connection import get_db
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth = OAuth2PasswordBearer(tokenUrl="/auth/login")

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

def create_password_reset_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=15)
    return jwt.encode({"sub": subject, "exp": expire, "type": "password_reset"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str, expected_type: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        if payload.get("type") != expected_type:
            return None

        return payload.get("sub")
    except InvalidTokenError:
        return None

def verify_dummy():
    pwd_context.dummy_verify() #Simulate a failed hash check


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id_str = decode_token(token, expected_type="access")
    if user_id_str is None:
        raise credentials_exception

    user = register_user.admin.get(db, id=user_id_str)
    if not user:
        raise credentials_exception

    return user


def get_current_active_user(
        current_user=Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    if not hasattr(current_user, 'is_confirmed') or not current_user.is_confirmed:
        raise HTTPException(status_code=403, detail="User email is not verified")

    return current_user