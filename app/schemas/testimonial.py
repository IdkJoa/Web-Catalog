from typing import Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from uuid import UUID

class TestimonialBase(BaseModel):
    name: str = Field(..., max_length=100)
    source: Optional[str] = Field(None, max_length=100)
    comment: str = Field(...)

class TestimonialCreate(TestimonialBase):
    pass

class TestimonialUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=4, max_length=100)
    source: Optional[str] = Field(None, max_length=100)
    comment: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class TestimonialOut(TestimonialBase):
    id: UUID
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

    model_config = {"from_attributes": True}