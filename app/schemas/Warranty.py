from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class WarrantyBase(BaseModel): #JD
    duration: str = Field(max_length=50, min_length=3,
                          description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    is_active: bool = True

class WarrantyOut(BaseModel): #JD
    id: UUID
    duration: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
