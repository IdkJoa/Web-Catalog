from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
import re
from uuid import UUID

from password_validator import PasswordValidator

class PasswordRecovery(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not schema.validate(value):
            raise ValueError(
                "Password must be at least 8 characters and contain an uppercase letter, lowercase letter, number, and symbol.")
        return value

class AdminUserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_and_format_name(cls, v: str) -> str:
        clean_name = v.strip()

        if not clean_name:
            raise ValueError("Name cannot be empty.")

        if not re.fullmatch(r"^[A-Za-z\s\-']+$", clean_name):
            raise ValueError("Name can only contain letters, spaces, hyphens, and apostrophes.")

        return clean_name.title()

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not schema.validate(value):
            raise ValueError("Password must be at least 8 characters and contain an uppercase letter, lowercase letter, number, and symbol.")
        return value

class AdminUserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None

class AdminUserOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    is_active: bool
    is_confirmed: bool
    model_config = ConfigDict(from_attributes=True)


schema = PasswordValidator()
schema.min(8).has().uppercase().lowercase().has().digits().has().symbols()