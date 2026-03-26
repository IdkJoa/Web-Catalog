from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class CapacityBase(BaseModel): #JD
    capacity: str = Field(max_length=50, min_length=3,
                          description="Debe contener al menos 3 caracteres y no mas de 50 caracteres")
    is_active: bool = True

class CapacityCreate(CapacityBase): #JD
    product_id: UUID = Field(not None)

class CapacityOut(CapacityBase): #JD
    id: UUID
    product_id: UUID
    model_config = ConfigDict(from_attributes=True)