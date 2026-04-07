import os
import shutil
import uuid
from typing import List, Any

from dotenv import load_dotenv
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.base.crud_base import CRUDBase
from app.models.models import Category
from app.schemas.category import CategoryBase

load_dotenv()
UPLOAD_DIR = os.getenv("UPLOAD_DIR")
BACKEND_DIR = os.getenv("BACKEND_DIR")
class Categoryservices(CRUDBase[Category, CategoryBase, CategoryBase]):


    def save_category_image(self, file: UploadFile) -> str:
        """Valida y guarda una imagen en disco, devolviendo su URL relativa."""
        dir_products = UPLOAD_DIR + "/category"
        if not os.path.exists(dir_products):
            os.makedirs(UPLOAD_DIR, exist_ok=True)

        print(dir_products)
        allowed_extensions = ["jpg", "jpeg", "png", "webp"]
        extension = file.filename.split(".")[-1].lower()

        if extension not in allowed_extensions:
            raise Exception( f"Extensión no permitida. Use: {allowed_extensions}")

        unique_filename = f"{uuid.uuid4()}.{extension}"
        file_path = os.path.join(dir_products, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return f"{BACKEND_DIR}/category/{unique_filename}"


    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Category]:
        try:
         stmt = select(Category).where(Category.is_active == True).offset(skip).limit(limit).order_by(Category.sort_order.desc())
         if stmt is None:
             return None

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











