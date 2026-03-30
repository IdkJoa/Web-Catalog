from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ConditionBase(BaseModel): #JD
    name: str = Field(max_length=50, min_length=3,
                      description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    description: Optional[str] = Field(max_length=500,
                                       description="No debe de pasar de 500 caracteres")
    sort_order: int = Field(default=1, description="Sort order")
    is_active: bool = True

class ConditionOut(ConditionBase):  # JD
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class ConditionProductsOut(BaseModel):  # JD
    name: str = Field(max_length=50, min_length=3)
