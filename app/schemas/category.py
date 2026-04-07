from typing import Optional
from uuid import UUID

from fastapi import Form, UploadFile, File
from pydantic import BaseModel, Field, ConfigDict


class CategoryBase(BaseModel): #JD
    name: str = Field(max_length=50, min_length=3,
                      description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    slug: str = Field(max_length=50, min_length=3,
                      description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    description: Optional[str] = Field(max_length=500,
                                       description="No debe de pasar de 500 caracteres")
    image_url: Optional[str] = None
    sort_order: int = Field(default=0, description="Sort order")
    is_active: bool = True
    meta_title: Optional[str] = Field(None, max_length=100)
    meta_description: Optional[str] = Field(None, max_length=160)
    meta_keywords: Optional[str] = Field(None, max_length=255)

class CategoryCreate:
    def __init__(
        self,
        name: str = Form(...),
        slug: str = Form(...),
        description: Optional[str] = Form(None),
        sort_order: int = Form(0),
        is_active: bool = Form(True),
        meta_title: Optional[str] = Form(None),
        meta_description: Optional[str] = Form(None),
        meta_keywords: Optional[str] = Form(None),
        image: UploadFile = File(...),
    ):
        self.name = name
        self.slug = slug
        self.description = description
        self.sort_order = sort_order
        self.is_active = is_active
        self.meta_title = meta_title
        self.meta_description = meta_description
        self.meta_keywords = meta_keywords
        self.image = image

class CategoryOut(CategoryBase): #JD
    id: UUID
    meta_title: Optional[str] = Field(None, max_length=100)
    meta_description: Optional[str] = Field(None, max_length=160)
    meta_keywords: Optional[str] = Field(None, max_length=255)
    model_config = ConfigDict(from_attributes=True)

class CategoryProductsOut(BaseModel):
    name: str = Field(max_length=50, min_length=3)
    meta_title: Optional[str] = Field(None, max_length=100)
    meta_description: Optional[str] = Field(None, max_length=160)
    meta_keywords: Optional[str] = Field(None, max_length=255)