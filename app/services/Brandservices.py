from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.base.crud_base import CRUDBase
from app.models.models import Brand
from app.schemas.Brand import BrandBase


class Brandservices(CRUDBase[Brand, BrandBase, BrandBase]):

    def get(self, db: Session, id: Any) -> Brand:
        try:
         stmt = (select(Brand).where(Brand.id == id, Brand.is_active == True))
         brand = db.execute(stmt).scalar_one_or_none()

         if brand is None:
            return None

         return brand
        except Exception as e:
            raise Exception(f"Error al devolver la brand: {str(e)}")

    def get_byname(self, db: Session, name: Any) -> Brand:
        try:
         stmt = select(Brand).where(Brand.name == name, Brand.is_active == True)
         brand = db.execute(stmt).scalar_one_or_none()

         if brand is None:
            return None

         return brand
        except Exception as e:
            raise Exception(f"Error al devolver la brand: {str(e)}")


brand_services = Brandservices(model=Brand)

