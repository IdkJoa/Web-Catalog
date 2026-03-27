from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
import uuid
from datetime import datetime

class BannerBase(BaseModel):
    title: str = Field(..., max_length=255)
    subtitle: Optional[str] = Field(None, max_length=255)
    image_url: str = Field(..., max_length=255, description="URL of the uploaded image")
    link: Optional[str] = Field(None, max_length=255, description="Where the banner clicks through to")
    sort_order: int = Field(default=0)
    is_active: bool = Field(default=True)

class BannerCreate(BannerBase):
    pass

class BannerUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    subtitle: Optional[str] = Field(None, max_length=255)
    image_url: Optional[str] = Field(None, max_length=255)
    link: Optional[str] = Field(None, max_length=255)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class BannerOut(BannerBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}