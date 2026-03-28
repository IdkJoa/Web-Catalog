import uuid
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class SiteSettingsBase(BaseModel):
    whatsapp: str = Field(..., max_length=15)
    address: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=50)
    meta_title: str = Field(..., max_length=50)
    meta_description: str = Field(..., max_length=50)
    meta_keywords: str = Field(..., max_length=50)

class SiteSettingsCreate(SiteSettingsBase):
    pass

class SiteSettingsUpdate(SiteSettingsBase):
    whatsapp: Optional[str] = Field(None, max_length=15)
    address: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=50)
    meta_title: Optional[str] = Field(None, max_length=50)
    meta_description: Optional[str] = Field(None, max_length=50)
    meta_keywords: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

class SiteSettingsOut(SiteSettingsBase):
    id: uuid.UUID
    is_active: Optional[bool] = None

    model_config = {"from_attributes": True}