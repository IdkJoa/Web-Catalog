import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional

from app.models.models import AdminUser
from app.models import models
from app.schemas.schemas import AdminUserCreate, AdminUserUpdate
from app.schemas import schemas
from app.core import security
from app.base.crud_base import CRUDBase

logger = logging.getLogger(__name__)

class RegisterUser(CRUDBase[AdminUser, AdminUserCreate, AdminUserUpdate]):
    # Overriding the standard create method to handle the password hashing
    def create(self, db: Session, *, obj_in: schemas.AdminUserCreate) -> models.AdminUser:
        logger.info(f"Registering new admin user: {obj_in.email}")
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
        logger.info(f"Successfully registered admin user with id: {db_obj.id}")
        return db_obj

    # Custom method specific only to Admins
    def get_by_email(self, db: Session, *, email: str) -> Optional[models.AdminUser]:
        logger.debug(f"Fetching admin user with email: {email}")
        stmt = select(models.AdminUser).where(models.AdminUser.email == email)
        return db.execute(stmt).scalar_one_or_none()

    def confirm_user(self, db: Session, *, db_obj: models.AdminUser) -> Optional[models.AdminUser]:
        logger.info(f"Confirming admin user with id: {db_obj.id}")
        db_obj.is_confirmed = True

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.info(f"Successfully confirmed admin user with id: {db_obj.id}")
        return db_obj

admin = RegisterUser(models.AdminUser)