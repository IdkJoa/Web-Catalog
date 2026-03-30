from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.base.crud_base import CRUDBase
from app.models.models import Capacity
from app.schemas.capacity import CapacityCreate, CapacityBase
from app.services.products_service import product_services


class Capacityservices(CRUDBase[Capacity, CapacityCreate, CapacityBase]):

    def get(self, db: Session, id: Any) -> Capacity:
        try:
         stmt = (select(Capacity).where(Capacity.id == id, Capacity.is_active == True))
         capacity = db.execute(stmt).scalar_one_or_none()

         if capacity is None:
            return None

         return capacity
        except Exception as e:
            raise Exception(f"Error al devolver la capacidad: {str(e)}")

    def get_byname(self, db: Session, capacity: Any) -> Capacity:
        try:
         stmt = (select(Capacity).where(Capacity.capacity == capacity, Capacity.is_active == True))
         capacity = db.execute(stmt).scalar_one_or_none()

         if capacity is None:
            return None

         return capacity
        except Exception as e:
            raise Exception(f"Error al devolver la capacidad: {str(e)}")

    def create(self, db: Session, *, obj_in: CapacityCreate) -> CapacityCreate:
        try:
          product = product_services.get(db=db, id=obj_in.product_id)

          if product is None:
              None

          db_obj = Capacity(
            product_id=product.id,
            capacity=obj_in.capacity,
            is_active=obj_in.is_active
          ) # Unpack and convert to instance of alquemy mode
          db.add(db_obj)
          db.commit()
          db.refresh(db_obj)
          return db_obj

        except Exception as e:
          raise Exception(f"Error al crear la capacidad: {str(e)}")


capacity_services = Capacityservices(model=Capacity)