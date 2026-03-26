from typing import Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from uuid import UUID

class TestimonialBase(BaseModel):
    author_name: str = Field(..., min_length=2, max_length=100, description="Name of the person leaving the review")
    author_title: Optional[str] = Field(None, max_length=100, description="Job title or company, e.g., 'CEO at TechCorp'")
    content: str = Field(..., min_length=10, max_length=1000, description="The actual review text")
    rating: Optional[int] = Field(5, ge=1, le=5, description="Star rating from 1 to 5")
    is_published: bool = Field(True, description="Allows admins to hide bad or spam reviews")
    avatar_url: Optional[HttpUrl] = Field(None, description="Optional link to their profile picture")

class TestimonialCreate(TestimonialBase):
    pass

class TestimonialUpdate(BaseModel):
    author_name: Optional[str] = Field(None, min_length=2, max_length=100)
    author_title: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = Field(None, min_length=10, max_length=1000)
    rating: Optional[int] = Field(None, ge=1, le=5)
    is_published: Optional[bool] = None
    avatar_url: Optional[HttpUrl] = None

class TestimonialOut(TestimonialBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}