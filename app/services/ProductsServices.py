from typing import Any, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.base.crud_base import CRUDBase
from app.models.models import Product
from app.schemas.Products import ProductBase, ProductCreate
from app.services.Brandservices import brand_services
from app.services.Categoryservices import category_service
from app.services.Conditionservices import condition_services
from app.services.Warrantyservices import warranty_services


class ProductsServices(CRUDBase[Product, ProductBase, ProductBase]):
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Product]:
        try:
         stmt = select(Product).where(Product.is_active == True).offset(skip).limit(limit).order_by(Product.price.desc())
         if stmt is None:
             return []

         return list(db.execute(stmt).scalars().all())

        except Exception as e:
         raise Exception(f"Error al listar Product: {str(e)}")

    def get(self, db: Session, id: Any) -> Product:
        try:
         stmt = (select(Product).where(Product.id == id, Product.is_active == True))
         category = db.execute(stmt).scalar_one_or_none()

         if category is None:
            return None

         return category
        except Exception as e:
            raise Exception(f"Error al devolver la Product: {str(e)}")

    def get_byname(self, db: Session, model_name: Any) -> Product:
        try:
         stmt = (select(Product).where(Product.model_name == model_name, Product.is_active == True))
         category = db.execute(stmt).scalar_one_or_none()

         if category is None:
            return None

         return category
        except Exception as e:
            raise Exception(f"Error al devolver la producto: {str(e)}")

    """
    Fslta listar por ofertas, categoria, marca
    """
    def get_byoffer(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Product]:
        try:
         stmt = (select(Product).where(Product.is_active == True, Product.sale_price.isnot(None), Product.sale_price < Product.price, Product.sale_price > 0)
                 .offset(skip).limit(limit).order_by(Product.sale_price.desc()))
         if stmt is None:
             return []

         return list(db.execute(stmt).scalars().all())

        except Exception as e:
         raise Exception(f"Error al listar Product by offer: {str(e)}")

    def get_by_category(self, db: Session, category_id: UUID, *, skip: int = 0, limit: int = 100) -> List[Product]:
        try:
            stmt = (
                select(Product)
                .where(
                    Product.is_active == True,
                    Product.category_id == category_id
                )
                .offset(skip).limit(limit)
                .order_by(Product.price.desc())
            )
            return list(db.execute(stmt).scalars().all())
        except Exception as e:
            raise Exception(f"Error al listar productos por categoria: {str(e)}")

    def get_by_brand(self, db: Session, brand_id: UUID, *, skip: int = 0, limit: int = 100) -> List[Product]:
        try:
            stmt = (
                select(Product)
                .where(
                    Product.is_active == True,
                    Product.brand_id == brand_id
                )
                .offset(skip).limit(limit)
                .order_by(Product.price.desc())
            )
            return list(db.execute(stmt).scalars().all())
        except Exception as e:
            raise Exception(f"Error al listar productos por marca: {str(e)}")

    def create(self, db: Session, *, obj_in: ProductCreate) -> ProductCreate:
        try:
          category = category_service.get(db=db, id=obj_in.category_id)
          warranty =warranty_services.get(db=db, id=obj_in.warranty_id)
          brand = brand_services.get(db=db, id=obj_in.brand_id)
          condition = condition_services.get(db=db, id=obj_in.condition_id)

          if category is None:
              raise Exception("Category not found")
          if warranty is None:
              raise Exception("Warranty not found")
          if brand is None:
              raise Exception("Brand not found")
          if condition is None:
              raise Exception("Condition not found")

          db_obj = Product(
            category_id=category.id,
            brand_id=brand.id,
            condition_id=condition.id,
            warranty_id=warranty.id,
            name=obj_in.name,
            image_url=obj_in.image_url,
            model_name=obj_in.model_name,
            price=obj_in.price,
            sale_price=obj_in.sale_price,
            stock_status=obj_in.stock_status,
            is_featured=obj_in.is_featured,
            is_active=obj_in.is_active
          ) # Unpack and convert to instance of alquemy model

          db.add(db_obj)
          db.commit()
          db.refresh(db_obj)
          return db_obj
        except Exception as e:
            raise Exception(f"Error al crear producto: {str(e)}")

product_services = ProductsServices(model=Product)

