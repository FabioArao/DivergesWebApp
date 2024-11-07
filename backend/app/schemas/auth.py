from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    phone_number: Optional[str] = None
    profile_picture: Optional[str] = None
    grade_level: Optional[str] = None
    subjects: Optional[str] = None
    
    @validator('grade_level')
    def validate_grade_level(cls, v, values):
        if values.get('role') == UserRole.STUDENT and not v:
            raise ValueError("Grade level is required for students")
        if values.get('role') != UserRole.STUDENT and v:
            raise ValueError("Grade level is only applicable for students")
        return v
    
    @validator('subjects')
    def validate_subjects(cls, v, values):
        if values.get('role') == UserRole.TEACHER and not v:
            raise ValueError("Subjects are required for teachers")
        if values.get('role') != UserRole.TEACHER and v:
            raise ValueError("Subjects are only applicable for teachers")
        return v

class UserCreate(UserBase):
    firebase_token: str

class UserResponse(UserBase):
    id: str
    firebase_uid: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    firebase_token: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_picture: Optional[str] = None
    grade_level: Optional[str] = None
    subjects: Optional[str] = None
    
    @validator('grade_level')
    def validate_grade_level_update(cls, v, values):
        if v is not None and not v.strip():
            raise ValueError("Grade level cannot be empty string")
        return v
    
    @validator('subjects')
    def validate_subjects_update(cls, v, values):
        if v is not None and not v.strip():
            raise ValueError("Subjects cannot be empty string")
        return v

class GuardianLinkRequest(BaseModel):
    student_id: str
    guardian_id: str

class StudentResponse(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    grade_level: str
    profile_picture: Optional[str] = None
    
    class Config:
        from_attributes = True

class TeacherResponse(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    subjects: str
    profile_picture: Optional[str] = None
    
    class Config:
        from_attributes = True

class GuardianResponse(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    profile_picture: Optional[str] = None
    students: List[StudentResponse]
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
