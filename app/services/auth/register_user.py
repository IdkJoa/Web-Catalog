from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional

from app.models.models import AdminUser
from app.models import models
from app.schemas.schemas import AdminUserCreate, AdminUserUpdate
from app.schemas import schemas
from app.core import security
from app.base.crud_base import CRUDBase

class RegisterUser(CRUDBase[AdminUser, AdminUserCreate, AdminUserUpdate]):
    # Overriding the standard create method to handle the password hashing
    def create(self, db: Session, *, obj_in: schemas.AdminUserCreate) -> models.AdminUser:
        hashed_pwd = security.hash_password(obj_in.password)

        db_obj = models.AdminUser(
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            email=obj_in.email,
            password=hashed_pwd,
            is_active=True,
            is_confirmed=False
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # Custom method specific only to Admins
    def get_by_email(self, db: Session, *, email: str) -> Optional[models.AdminUser]:
        stmt = select(models.AdminUser).where(models.AdminUser.email == email)
        return db.execute(stmt).scalar_one_or_none()

    def confirm_user(self, db: Session, *, db_obj: models.AdminUser) -> Optional[models.AdminUser]:
        db_obj.is_confirmed = True

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

admin = RegisterUser(models.AdminUser)