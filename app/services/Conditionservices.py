from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.base.crud_base import CRUDBase
from app.models.models import Condition
from app.schemas.Condition import ConditionBase


class Conditionservices(CRUDBase[Condition, ConditionBase, ConditionBase]):

    def get(self, db: Session, id: Any) -> Condition:
        try:
         stmt = (select(Condition).where(Condition.id == id, Condition.is_active == True))
         condition = db.execute(stmt).scalar_one_or_none()

         if condition is None:
            return None

         return condition
        except Exception as e:
            raise Exception(f"Error al devolver la Condition: {str(e)}")

    def get_byname(self, db: Session, name: Any) -> Condition:
        try:
         stmt = select(Condition).where(Condition.name == name, Condition.is_active == True)
         condition = db.execute(stmt).scalar_one_or_none()

         if condition is None:
            return None

         return condition
        except Exception as e:
            raise Exception(f"Error al devolver la Condition: {str(e)}")

condition_services = Conditionservices(model=Condition)