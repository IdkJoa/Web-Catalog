from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.db_connection import get_db
from app.models import models
import app.core.security as security

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db())
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = security.decode_token(token, expected_type="access")

    if user_id is None:
        raise credentials_exception

    query = select(models.AdminUser).where(models.AdminUser.id == user_id)
    user = db.execute(query).scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user