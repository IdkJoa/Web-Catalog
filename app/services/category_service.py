import logging
from typing import List, Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.base.crud_base import CRUDBase
from app.models.models import Category
from app.schemas.category import CategoryBase

logger = logging.getLogger(__name__)

class Categoryservices(CRUDBase[Category, CategoryBase, CategoryBase]):

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Category]:
        logger.debug(f"Fetching multiple categories (skip={skip}, limit={limit})")
        try:
         stmt = select(Category).where(Category.is_active == True).offset(skip).limit(limit).order_by(Category.sort_order.desc())
         return list(db.execute(stmt).scalars().all())

        except Exception as e:
         logger.error(f"Error listing categories: {str(e)}")
         raise Exception(f"Error al listar categorias: {str(e)}")

    def get(self, db: Session, id: Any) -> Optional[Category]:
        logger.debug(f"Fetching category with id: {id}")
        try:
         stmt = (select(Category).where(Category.id == id, Category.is_active == True))
         category = db.execute(stmt).scalar_one_or_none()

         if category is None:
            logger.debug(f"Category with id {id} not found")
            return None

         return category
        except Exception as e:
            logger.error(f"Error fetching category with id {id}: {str(e)}")
            raise Exception(f"Error al devolver la categoria: {str(e)}")

    def get_byname(self, db: Session, name: Any) -> Optional[Category]:
        logger.debug(f"Fetching category with name: {name}")
        try:
         stmt = (select(Category).where(Category.name == name, Category.is_active == True))
         category = db.execute(stmt).scalar_one_or_none()

         if category is None:
            logger.debug(f"Category with name {name} not found")
            return None

         return category
        except Exception as e:
            logger.error(f"Error fetching category with name {name}: {str(e)}")
            raise Exception(f"Error al devolver la categoria: {str(e)}")

    def create(self, db: Session, *, obj_in: CategoryBase) -> Category:
        logger.info(f"Creating new category: {obj_in.name}")
        try:
         if obj_in.sort_order < 1:
            logger.warning(f"Invalid sort order: {obj_in.sort_order}")
            raise Exception(f"Sort order invalido")

         db_obj = Category(
            name=obj_in.name,
            slug=obj_in.slug,
            description=obj_in.description,
            image_url=obj_in.image_url,
            sort_order=obj_in.sort_order,
            is_active=obj_in.is_active,

         ) # Unpack and convert to instance of alquemy model
         db.add(db_obj)
         db.commit()
         db.refresh(db_obj)
         logger.info(f"Successfully created category with id: {db_obj.id}")
         return db_obj
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            raise Exception(f"Error al crear categoria: {str(e)}")

category_service = Categoryservices(model=Category)











