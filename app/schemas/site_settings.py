import uuid
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class SiteSettingsBase(BaseModel):
    whatsapp: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None)
    email: Optional[EmailStr] = Field(None, max_length=255)
    open_time: Optional[str] = Field(None, description="Opening time in HH:MM format", max_length=5)
    close_time: Optional[str] = Field(None, description="Closing time in HH:MM format", max_length=5)
    meta_title: Optional[str] = Field(None, max_length=100)
    meta_description: Optional[str] = Field(None, max_length=160)
    meta_keywords: Optional[str] = Field(None, max_length=255)

class SiteSettingsCreate(SiteSettingsBase):
    pass

class SiteSettingsUpdate(SiteSettingsBase):
    is_active: Optional[bool] = None

class SiteSettingsOut(SiteSettingsBase):
    id: uuid.UUID
    is_active: Optional[bool] = None

    model_config = {"from_attributes": True}