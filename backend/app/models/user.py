from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import validates
import enum
import re
from .base import BaseModel

class UserRole(enum.Enum):
    STUDENT = 'student'
    TEACHER = 'teacher'
    GUARDIAN = 'guardian'

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, nullable=False, unique=True)
    firebase_uid = Column(String, unique=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    first_name = Column(String)
    last_name = Column(String)

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise ValueError('Email is required')
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError('Invalid email format')
        
        return email.lower()

    @validates('role')
    def validate_role(self, key, role):
        if isinstance(role, str):
            try:
                return UserRole[role.upper()]
            except KeyError:
                raise ValueError(f'Invalid role: {role}. Must be one of {[r.value for r in UserRole]}')
        return role

    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'role': self.role.value if self.role else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
