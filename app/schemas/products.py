from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

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
    sale_price: Optional[Decimal] = Field(ge=1, decimal_places=4, description="Debe ser mayor a 0")
    stock_status: bool = True
    is_featured: bool = False
    is_active: bool = True


class ProductCreate(ProductBase):  # JD
    pass


class ProductUpdate(BaseModel):  # JD
    name: Optional[str] | None = Field(max_length=50, min_length=3,
                                       description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    stock_status: Optional[bool] = None
    price: Optional[Decimal] | None = Field(ge=1, decimal_places=4, description="Debe ser mayor a 0")
    sale_price: Optional[Decimal] | None = Field(ge=1, decimal_places=4, description="Debe ser mayor a 0")
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