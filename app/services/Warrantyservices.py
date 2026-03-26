from typing import List, Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.base.crud_base import CRUDBase
from app.models.models import Warranty
from app.schemas.Warranty import WarrantyBase


class Warrantyservices(CRUDBase[Warranty, WarrantyBase, WarrantyBase]):
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Warranty]:
        try:
         stmt = select(Warranty).where(Warranty.is_active == True).offset(skip).limit(limit).order_by(Warranty.created_at.desc())
         if stmt is None:
             return []

         return list(db.execute(stmt).scalars().all())

        except Exception as e:
         raise Exception(f"Error al listar garantias: {str(e)}")

    def get(self, db: Session, id: Any) -> Warranty:
        try:
         stmt = (select(Warranty).where(Warranty.id == id, Warranty.is_active == True))
         warranty = db.execute(stmt).scalar_one_or_none()

         if warranty is None:
            return None

         return warranty
        except Exception as e:
            raise Exception(f"Error al devolver la garantia: {str(e)}")

    def get_byduration(self, db: Session, duration: Any) -> Warranty:
        try:
         stmt = (select(Warranty).where(Warranty.duration == duration, Warranty.is_active == True))
         warranty = db.execute(stmt).scalar_one_or_none()

         if warranty is None:
            return None

         return warranty
        except Exception as e:
            raise Exception(f"Error al devolver la garantia: {str(e)}")

warranty_services = Warrantyservices(model=Warranty)