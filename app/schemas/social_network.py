import uuid

from pydantic import Field
from typing import Optional

from pydantic import BaseModel


class SocialNetworkBase(BaseModel):
    name: str = Field(..., max_length=100)
    url: str = Field(..., max_length=255)

class SocialNetworkCreate(SocialNetworkBase):
    pass

class SocialNetworkUpdate(BaseModel):
    name: Optional[str]
    url: Optional[str]
    is_active: Optional[bool]

class SocialNetworkOut(SocialNetworkBase):
    id: uuid.UUID
    is_active: bool

    model_config = {"from_attributes": True}