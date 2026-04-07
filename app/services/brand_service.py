import logging
import os
import shutil
import uuid
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.base.crud_base import CRUDBase
from app.models.models import Brand
from app.schemas.brand import BrandBase

logger = logging.getLogger(__name__)
load_dotenv()
UPLOAD_DIR = os.getenv("UPLOAD_DIR")
BACKEND_DIR = os.getenv("BACKEND_DIR")
class Brandservices(CRUDBase[Brand, BrandBase, BrandBase]):

    def save_brand_image(self, file: UploadFile) -> str:
        """Valida y guarda una imagen en disco, devolviendo su URL relativa."""
        dir_products = UPLOAD_DIR + "/brands"
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

        return f"{BACKEND_DIR}/brands/{unique_filename}"

    def get(self, db: Session, id: Any) -> Optional[Brand]:
        logger.debug(f"Fetching Brand with id: {id}")
        try:
         stmt = (select(Brand).where(Brand.id == id, Brand.is_active == True))
         brand = db.execute(stmt).scalar_one_or_none()

         if brand is None:
            logger.debug(f"Brand with id {id} not found")
            return None

         return brand
        except Exception as e:
            logger.error(f"Error fetching brand with id {id}: {str(e)}")
            raise Exception(f"Error al devolver la brand: {str(e)}")

    def get_byname(self, db: Session, name: Any) -> Optional[Brand]:
        logger.debug(f"Fetching Brand with name: {name}")
        try:
         stmt = select(Brand).where(Brand.name == name, Brand.is_active == True)
         brand = db.execute(stmt).scalar_one_or_none()

         if brand is None:
            logger.debug(f"Brand with name {name} not found")
            return None

         return brand
        except Exception as e:
            logger.error(f"Error fetching brand with name {name}: {str(e)}")
            raise Exception(f"Error al devolver la brand: {str(e)}")


brand_services = Brandservices(model=Brand)

