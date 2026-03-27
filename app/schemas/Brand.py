from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class BrandBase(BaseModel):
    name: str = Field(max_length=50, min_length=3,
                      description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    slug: str = Field(max_length=50, min_length=3,
                      description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    image_url: Optional[str] = None
    is_active: bool = True

class BrandOut(BrandBase): #JD
    id: UUID
    model_config = ConfigDict(from_attributes=True)