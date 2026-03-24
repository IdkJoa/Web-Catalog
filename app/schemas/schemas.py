from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class BrandBase(BaseModel):
    name: str
    slug: str
    image_url: Optional[str] = None
    is_active: bool = True

class ConditionBase(BaseModel):
    name: str
    description: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class WarrantyBase(BaseModel):
    duration: str
    is_active: bool = True

class CapacityBase(BaseModel):
    capacity: str
    is_active: bool = True

class CapacityCreate(CapacityBase):
    product_id: UUID

class CapacityOut(CapacityBase):
    id: UUID
    product_id: UUID
    model_config = ConfigDict(from_attributes=True)

class ProductBase(BaseModel):
    category_id: UUID
    brand_id: UUID
    condition_id: UUID
    warranty_id: UUID
    name: str
    image_url: Optional[str] = None
    model_name: Optional[str] = None
    price: float
    sale_price: Optional[float] = None
    stock_status: bool = True
    is_featured: bool = False
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None

class CategoryOut(CategoryBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class BrandOut(BrandBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class ConditionOut(ConditionBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class WarrantyOut(WarrantyBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProductOut(ProductBase):
    id: UUID
    updated_at: datetime
    category: Optional[CategoryOut] = None
    brand: Optional[BrandOut] = None
    capacities: List[CapacityOut] = []
    model_config = ConfigDict(from_attributes=True)

class AdminUserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class AdminUserOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    is_active: bool
    model_config = ConfigDict(from_attributes=True)