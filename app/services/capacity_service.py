import logging
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.base.crud_base import CRUDBase
from app.models.models import Capacity
from app.schemas.capacity import CapacityCreate, CapacityBase
from app.services.products_service import product_services

logger = logging.getLogger(__name__)

class Capacityservices(CRUDBase[Capacity, CapacityCreate, CapacityBase]):

    def get(self, db: Session, id: Any) -> Optional[Capacity]:
        logger.debug(f"Fetching Capacity with id: {id}")
        try:
         stmt = (select(Capacity).where(Capacity.id == id, Capacity.is_active == True))
         capacity = db.execute(stmt).scalar_one_or_none()

         if capacity is None:
            logger.debug(f"Capacity with id {id} not found")
            return None

         return capacity
        except Exception as e:
            logger.error(f"Error fetching capacity with id {id}: {str(e)}")
            raise Exception(f"Error al devolver la capacidad: {str(e)}")

    def get_byname(self, db: Session, capacity: Any) -> Optional[Capacity]:
        logger.debug(f"Fetching Capacity with name: {capacity}")
        try:
         stmt = (select(Capacity).where(Capacity.capacity == capacity, Capacity.is_active == True))
         capacity = db.execute(stmt).scalar_one_or_none()

         if capacity is None:
            logger.debug(f"Capacity with name {capacity} not found")
            return None

         return capacity
        except Exception as e:
            logger.error(f"Error fetching capacity with name {capacity}: {str(e)}")
            raise Exception(f"Error al devolver la capacidad: {str(e)}")

    def create(self, db: Session, *, obj_in: CapacityCreate) -> Capacity:
        logger.info(f"Creating new Capacity for product_id: {obj_in.product_id}")
        try:
          product = product_services.get(db=db, id=obj_in.product_id)

          if product is None:
              logger.warning(f"Failed to create Capacity: Product with id {obj_in.product_id} not found")
              return None

          db_obj = Capacity(
            product_id=product.id,
            capacity=obj_in.capacity,
            is_active=obj_in.is_active
          ) # Unpack and convert to instance of alquemy mode
          db.add(db_obj)
          db.commit()
          db.refresh(db_obj)
          logger.info(f"Successfully created Capacity with id: {db_obj.id}")
          return db_obj

        except Exception as e:
          logger.error(f"Error creating capacity: {str(e)}")
          raise Exception(f"Error al crear la capacidad: {str(e)}")


capacity_services = Capacityservices(model=Capacity)