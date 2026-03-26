from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID


class AdminUserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class AdminUserOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    is_active: bool
    model_config = ConfigDict(from_attributes=True)