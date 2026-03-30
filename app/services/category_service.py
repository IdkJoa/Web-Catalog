from typing import List, Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.base.crud_base import CRUDBase
from app.models.models import Category
from app.schemas.category import CategoryBase


class Categoryservices(CRUDBase[Category, CategoryBase, CategoryBase]):

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Category]:
        try:
         stmt = select(Category).where(Category.is_active == True).offset(skip).limit(limit).order_by(Category.sort_order.desc())
         if stmt is None:
             return []

         return list(db.execute(stmt).scalars().all())

        except Exception as e:
         raise Exception(f"Error al listar categorias: {str(e)}")

    def get(self, db: Session, id: Any) -> Category:
        try:
         stmt = (select(Category).where(Category.id == id, Category.is_active == True))
         category = db.execute(stmt).scalar_one_or_none()

         if category is None:
            return None

         return category
        except Exception as e:
            raise Exception(f"Error al devolver la categoria: {str(e)}")

    def get_byname(self, db: Session, name: Any) -> Category:
        try:
         stmt = (select(Category).where(Category.name == name, Category.is_active == True))
         category = db.execute(stmt).scalar_one_or_none()

         if category is None:
            return None

         return category
        except Exception as e:
            raise Exception(f"Error al devolver la categoria: {str(e)}")

    def create(self, db: Session, *, obj_in: CategoryBase) -> CategoryBase:
        try:
         if obj_in.sort_order < 1:
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
         return db_obj
        except Exception as e:
            raise Exception(f"Error al crear categoria: {str(e)}")

category_service = Categoryservices(model=Category)











