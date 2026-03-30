import logging
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.base.crud_base import CRUDBase
from app.models.models import Condition
from app.schemas.condition import ConditionBase

logger = logging.getLogger(__name__)

class Conditionservices(CRUDBase[Condition, ConditionBase, ConditionBase]):

    def get(self, db: Session, id: Any) -> Optional[Condition]:
        logger.debug(f"Fetching Condition with id: {id}")
        try:
         stmt = (select(Condition).where(Condition.id == id, Condition.is_active == True))
         condition = db.execute(stmt).scalar_one_or_none()

         if condition is None:
            logger.debug(f"Condition with id {id} not found")
            return None

         return condition
        except Exception as e:
            logger.error(f"Error fetching condition with id {id}: {str(e)}")
            raise Exception(f"Error al devolver la Condition: {str(e)}")

    def get_byname(self, db: Session, name: Any) -> Optional[Condition]:
        logger.debug(f"Fetching Condition with name: {name}")
        try:
         stmt = select(Condition).where(Condition.name == name, Condition.is_active == True)
         condition = db.execute(stmt).scalar_one_or_none()

         if condition is None:
            logger.debug(f"Condition with name {name} not found")
            return None

         return condition
        except Exception as e:
            logger.error(f"Error fetching condition with name {name}: {str(e)}")
            raise Exception(f"Error al devolver la Condition: {str(e)}")

condition_services = Conditionservices(model=Condition)