from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from fastapi import Form, UploadFile, File
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.brand import BrandProductOut
from app.schemas.capacity import CapacityOut, CapacityProductOut
from app.schemas.category import CategoryProductsOut
from app.schemas.condition import ConditionProductsOut
from app.schemas.warranty import WarrantyProductsOut


class ProductBase(BaseModel):  # JD
    category_id: UUID
    brand_id: UUID
    condition_id: UUID
    warranty_id: UUID
    name: str = Field(max_length=50, min_length=3,
                      description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    image_url: Optional[str] = None
    model_name: Optional[str] | None = Field(max_length=50, min_length=3,
                                             description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    price: Decimal | None = Field(ge=1, decimal_places=4, description="Debe ser mayor a 0")
    sale_price: Optional[Decimal] = Field(ge=0, decimal_places=4, description="Debe ser mayor a 0")
    stock_status: bool = True
    is_featured: bool = False
    is_active: bool = True


class ProductsCreate:
    def __init__(
        self,
        category_id: UUID = Form(...),
        brand_id: UUID = Form(...),
        condition_id: UUID = Form(...),
        warranty_id: UUID = Form(...),

        name: str = Form(...),
        model_name: Optional[str] = Form(None),

        price: Optional[float] = Form(None),
        sale_price: Optional[float] = Form(None),

        stock_status: bool = Form(True),
        is_featured: bool = Form(False),
        is_active: bool = Form(True),

        image: UploadFile = File(...)
    ):
        self.category_id = category_id
        self.brand_id = brand_id
        self.condition_id = condition_id
        self.warranty_id = warranty_id

        self.name = name
        self.model_name = model_name

        self.price = price
        self.sale_price = sale_price

        self.stock_status = stock_status
        self.is_featured = is_featured
        self.is_active = is_active

        self.image = image


class ProductUpdate(BaseModel):  # JD
    name: Optional[str] | None = Field(max_length=50, min_length=3,
                                       description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    stock_status: Optional[bool] = None
    price: Optional[Decimal] | None = Field(ge=1, decimal_places=4, description="Debe ser mayor a 0")
    sale_price: Optional[Decimal] | None = Field(ge=0, decimal_places=4, description="Debe ser mayor a 0")
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    meta_title: Optional[str] = Field(None, max_length=100)
    meta_description: Optional[str] = Field(None, max_length=160)
    meta_keywords: Optional[str] = Field(None, max_length=255)


class ProductOut(ProductBase):  # JD
    id: UUID
    updated_at: datetime
    category: Optional[CategoryProductsOut] = None
    brand: Optional[BrandProductOut] = None
    condition: Optional[ConditionProductsOut] = None
    warranty: Optional[WarrantyProductsOut] = None
    capacities: List[CapacityProductOut] = []
    meta_title: Optional[str] = Field(None, max_length=100)
    meta_description: Optional[str] = Field(None, max_length=160)
    meta_keywords: Optional[str] = Field(None, max_length=255)
    model_config = ConfigDict(from_attributes=True)