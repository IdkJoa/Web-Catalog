import logging
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.base.crud_base import CRUDBase
from app.models.models import Brand
from app.schemas.brand import BrandBase

logger = logging.getLogger(__name__)

class Brandservices(CRUDBase[Brand, BrandBase, BrandBase]):

    def get(self, db: Session, id: Any) -> Optional[Brand]:
        logger.debug(f"Fetching Brand with id: {id}")
        try:
         stmt = (select(Brand).where(Brand.id == id, Brand.is_active == True))
         brand = db.execute(stmt).scalar_one_or_none()

         if brand is None:
            logger.debug(f"Brand with id {id} not found")
            return None

         return brand
        except Exception as e:
            logger.error(f"Error fetching brand with id {id}: {str(e)}")
            raise Exception(f"Error al devolver la brand: {str(e)}")

    def get_byname(self, db: Session, name: Any) -> Optional[Brand]:
        logger.debug(f"Fetching Brand with name: {name}")
        try:
         stmt = select(Brand).where(Brand.name == name, Brand.is_active == True)
         brand = db.execute(stmt).scalar_one_or_none()

         if brand is None:
            logger.debug(f"Brand with name {name} not found")
            return None

         return brand
        except Exception as e:
            logger.error(f"Error fetching brand with name {name}: {str(e)}")
            raise Exception(f"Error al devolver la brand: {str(e)}")


brand_services = Brandservices(model=Brand)

