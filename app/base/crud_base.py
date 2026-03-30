import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models.models import Base

# Set up logging for the module
logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        logger.debug(f"Fetching {self.model.__name__} with id: {id}")
        stmt = select(self.model).where(self.model.id == id, self.model.is_active == True)
        return db.execute(stmt).scalar_one_or_none()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        logger.debug(f"Fetching multiple {self.model.__name__} (skip={skip}, limit={limit})")
        stmt = select(self.model).where(self.model.is_active == True).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def get_all_no_filtered(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        logger.debug(f"Fetching all {self.model.__name__} (no filtering, skip={skip}, limit={limit})")
        stmt = select(self.model).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        logger.info(f"Creating new {self.model.__name__}")
        obj_in_data = jsonable_encoder(obj_in) # Gets the schema and convert into dict
        db_obj = self.model(**obj_in_data) # Unpack and convert to instance of alquemy model
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.info(f"Successfully created {self.model.__name__} with id: {getattr(db_obj, 'id', 'N/A')}")
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        obj_id = getattr(db_obj, 'id', 'N/A')
        logger.info(f"Updating {self.model.__name__} with id: {obj_id}")
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.info(f"Successfully updated {self.model.__name__} with id: {obj_id}")
        return db_obj

    def delete(self, db: Session, *, id: Any) -> Optional[ModelType]:
        logger.info(f"Deleting (soft delete) {self.model.__name__} with id: {id}")
        stmt = select(self.model).where(self.model.id == id)
        obj = db.execute(stmt).scalar_one_or_none()
        if obj and hasattr(obj, 'is_active'):
            obj.is_active = False
            db.add(obj)
            db.commit()
            db.refresh(obj)
            logger.info(f"Successfully deleted {self.model.__name__} with id: {id}")
        else:
            logger.warning(f"Attempted to delete {self.model.__name__} with id: {id} but it was not found or lacks is_active field")
        return obj


