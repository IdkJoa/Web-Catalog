from pydantic import BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class CategoryBase(BaseModel): #JD
    name: str = Field(max_length=50, min_length=3,
                      description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    slug: str = Field(max_length=50, min_length=3,
                      description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    description: Optional[str] = Field(max_length=500,
                                       description="No debe de pasar de 500 caracteres")
    image_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class BrandBase(BaseModel):
    name: str = Field(max_length=50, min_length=3,
                      description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    slug: str = Field(max_length=50, min_length=3,
                      description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    image_url: Optional[str] = None
    is_active: bool = True

class ConditionBase(BaseModel): #JD
    name: str = Field(max_length=50, min_length=3,
                      description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    description: Optional[str] = Field(max_length=500,
                                       description="No debe de pasar de 500 caracteres")
    sort_order: int = 0
    is_active: bool = True

class WarrantyBase(BaseModel): #JD
    duration: str = Field(max_length=50, min_length=3,
                          description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    is_active: bool = True

class CapacityBase(BaseModel): #JD
    capacity: str = Field(max_length=50, min_length=3,
                          description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    is_active: bool = True

class CapacityCreate(CapacityBase): #JD
    product_id: UUID = Field(not None)

class CapacityOut(CapacityBase): #JD
    id: UUID
    product_id: UUID
    model_config = ConfigDict(from_attributes=True)

class ProductBase(BaseModel): #JD
    category_id: UUID
    brand_id: UUID
    condition_id: UUID
    warranty_id: UUID
    name: str = Field(max_length=50, min_length=3,
                      description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    image_url: Optional[str] = None
    model_name: Optional[str] | None = Field(max_length=50, min_length=3,
                                             description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    price: float | None = Field(ge=1, decimal_places=4, description="Debe ser mayor a 0")
    sale_price: Optional[float] = Field(ge=1, decimal_places=4, description="Debe ser mayor a 0")
    stock_status: bool = True
    is_featured: bool = False
    is_active: bool = True

class ProductCreate(ProductBase): #JD
    pass

class ProductUpdate(BaseModel): #JD
    name: Optional[str] | None = Field(max_length=50, min_length=3,
                      description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    price: Optional[float] | None = Field(ge=1, decimal_places=4, description="Debe ser mayor a 0")
    is_active: Optional[bool] = None

class CategoryOut(CategoryBase): #JD
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class BrandOut(BrandBase): #JD
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class ConditionOut(ConditionBase): #JD
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class WarrantyOut(WarrantyBase): #JD
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProductOut(ProductBase): #JD
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