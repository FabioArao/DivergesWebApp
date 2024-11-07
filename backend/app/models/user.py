from sqlalchemy import Column, String, Enum, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base
from typing import Optional, List
import uuid

class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    GUARDIAN = "guardian"
    ADMIN = "admin"

# Association table for guardian-student relationship
guardian_student = Table(
    'guardian_student',
    Base.metadata,
    Column('guardian_id', String, ForeignKey('users.id')),
    Column('student_id', String, ForeignKey('users.id'))
)

# Association table for teacher-student relationship
teacher_student = Table(
    'teacher_student',
    Base.metadata,
    Column('teacher_id', String, ForeignKey('users.id')),
    Column('student_id', String, ForeignKey('users.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    firebase_uid = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Profile fields
    phone_number = Column(String)
    profile_picture = Column(String)
    
    # Role-specific fields
    grade_level = Column(String)  # For students
    subjects = Column(String)     # For teachers
    
    # Relationships
    students_as_guardian = relationship(
        "User",
        secondary=guardian_student,
        primaryjoin=(id == guardian_student.c.guardian_id),
        secondaryjoin=(id == guardian_student.c.student_id),
        backref="guardians"
    )
    
    students_as_teacher = relationship(
        "User",
        secondary=teacher_student,
        primaryjoin=(id == teacher_student.c.teacher_id),
        secondaryjoin=(id == teacher_student.c.student_id),
        backref="teachers"
    )

    def __init__(self, firebase_uid: str, email: str, full_name: str, role: UserRole, **kwargs):
        self.firebase_uid = firebase_uid
        self.email = email
        self.full_name = full_name
        self.role = role
        
        # Set optional fields
        self.phone_number = kwargs.get('phone_number')
        self.profile_picture = kwargs.get('profile_picture')
        self.grade_level = kwargs.get('grade_level')
        self.subjects = kwargs.get('subjects')
        
    @property
    def is_student(self) -> bool:
        return self.role == UserRole.STUDENT
        
    @property
    def is_teacher(self) -> bool:
        return self.role == UserRole.TEACHER
        
    @property
    def is_guardian(self) -> bool:
        return self.role == UserRole.GUARDIAN
        
    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
    
    def can_view_student(self, student_id: str) -> bool:
        """Check if user has permission to view a student's information"""
        if self.is_admin:
            return True
        if self.is_student:
            return self.id == student_id
        if self.is_teacher:
            return any(s.id == student_id for s in self.students_as_teacher)
        if self.is_guardian:
            return any(s.id == student_id for s in self.students_as_guardian)
        return False
    
    def can_upload_content(self) -> bool:
        """Check if user has permission to upload educational content"""
        return self.is_teacher or self.is_admin
    
    def can_manage_users(self) -> bool:
        """Check if user has permission to manage other users"""
        return self.is_admin
    
    def to_dict(self) -> dict:
        """Convert user object to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "is_active": self.is_active,
            "phone_number": self.phone_number,
            "profile_picture": self.profile_picture,
            "grade_level": self.grade_level if self.is_student else None,
            "subjects": self.subjects if self.is_teacher else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
