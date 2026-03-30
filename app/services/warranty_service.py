import logging
from typing import List, Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.base.crud_base import CRUDBase
from app.models.models import Warranty
from app.schemas.warranty import WarrantyBase

logger = logging.getLogger(__name__)

class Warrantyservices(CRUDBase[Warranty, WarrantyBase, WarrantyBase]):
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Warranty]:
        logger.debug(f"Fetching multiple warranties (skip={skip}, limit={limit})")
        try:
         stmt = select(Warranty).where(Warranty.is_active == True).offset(skip).limit(limit).order_by(Warranty.created_at.desc())
         return list(db.execute(stmt).scalars().all())

        except Exception as e:
         logger.error(f"Error listing warranties: {str(e)}")
         raise Exception(f"Error al listar garantias: {str(e)}")

    def get(self, db: Session, id: Any) -> Optional[Warranty]:
        logger.debug(f"Fetching warranty with id: {id}")
        try:
         stmt = (select(Warranty).where(Warranty.id == id, Warranty.is_active == True))
         warranty = db.execute(stmt).scalar_one_or_none()

         if warranty is None:
            logger.debug(f"Warranty with id {id} not found")
            return None

         return warranty
        except Exception as e:
            logger.error(f"Error fetching warranty with id {id}: {str(e)}")
            raise Exception(f"Error al devolver la garantia: {str(e)}")

    def get_byduration(self, db: Session, duration: Any) -> Optional[Warranty]:
        logger.debug(f"Fetching warranty with duration: {duration}")
        try:
         stmt = (select(Warranty).where(Warranty.duration == duration, Warranty.is_active == True))
         warranty = db.execute(stmt).scalar_one_or_none()

         if warranty is None:
            logger.debug(f"Warranty with duration {duration} not found")
            return None

         return warranty
        except Exception as e:
            logger.error(f"Error fetching warranty with duration {duration}: {str(e)}")
            raise Exception(f"Error al devolver la garantia: {str(e)}")

warranty_services = Warrantyservices(model=Warranty)