from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from ..models.user import UserRole

class TokenSchema(BaseModel):
    token: str

    @validator('token')
    def token_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Token must not be empty')
        return v

class UserBase(BaseModel):
    email: EmailStr
    role: UserRole
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ErrorResponse(BaseModel):
    detail: str
    code: str
