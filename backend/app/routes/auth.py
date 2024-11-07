from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db_session
from app.config.firebase import verify_firebase_token
from app.models.user import User, UserRole
from app.schemas.auth import (
    UserCreate, UserResponse, UserLogin, UserUpdate,
    GuardianLinkRequest, StudentResponse, TeacherResponse,
    GuardianResponse, ErrorResponse
)
from app.dependencies import (
    get_current_user, get_admin_user, get_teacher_user,
    get_guardian_user, get_student_access,
    get_user_management_permission
)
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, responses={400: {"model": ErrorResponse}})
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db_session)
):
    """Register a new user"""
    try:
        # Verify Firebase token
        decoded_token = verify_firebase_token(user_data.firebase_token)
        firebase_uid = decoded_token['uid']
        email = decoded_token['email']
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered"
            )
        
        # Create new user
        user = User(
            firebase_uid=firebase_uid,
            email=email,
            full_name=user_data.full_name,
            role=user_data.role,
            phone_number=user_data.phone_number,
            profile_picture=user_data.profile_picture,
            grade_level=user_data.grade_level,
            subjects=user_data.subjects
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"New user registered: {user.email} with role {user.role}")
        return user
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=UserResponse, responses={401: {"model": ErrorResponse}})
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db_session)
):
    """Login user"""
    try:
        # Verify Firebase token
        decoded_token = verify_firebase_token(login_data.firebase_token)
        
        # Get user from database
        user = db.query(User).filter(User.firebase_uid == decoded_token['uid']).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not registered"
            )
            
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        logger.info(f"User logged in: {user.email}")
        return user
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Update current user information"""
    try:
        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(current_user, field, value)
        
        db.commit()
        db.refresh(current_user)
        return current_user
        
    except Exception as e:
        logger.error(f"Update user error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/students", response_model=List[StudentResponse])
async def get_accessible_students(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get list of students accessible to current user"""
    if current_user.is_admin:
        students = db.query(User).filter(User.role == UserRole.STUDENT).all()
    elif current_user.is_teacher:
        students = current_user.students_as_teacher
    elif current_user.is_guardian:
        students = current_user.students_as_guardian
    elif current_user.is_student:
        students = [current_user]
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view students"
        )
    
    return students

@router.post("/link-guardian", status_code=status.HTTP_201_CREATED)
async def link_guardian_to_student(
    link_data: GuardianLinkRequest,
    _: bool = Depends(get_user_management_permission),
    db: Session = Depends(get_db_session)
):
    """Link a guardian to a student"""
    student = db.query(User).filter(User.id == link_data.student_id).first()
    guardian = db.query(User).filter(User.id == link_data.guardian_id).first()
    
    if not student or not guardian:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student or guardian not found"
        )
    
    if student.role != UserRole.STUDENT or guardian.role != UserRole.GUARDIAN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role combination"
        )
    
    guardian.students_as_guardian.append(student)
    db.commit()
    
    return {"message": "Guardian linked to student successfully"}

@router.get("/teachers", response_model=List[TeacherResponse])
async def get_teachers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get list of teachers"""
    teachers = db.query(User).filter(User.role == UserRole.TEACHER).all()
    return teachers

@router.get("/guardians", response_model=List[GuardianResponse])
async def get_guardians(
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db_session)
):
    """Get list of guardians (admin only)"""
    guardians = db.query(User).filter(User.role == UserRole.GUARDIAN).all()
    return guardians

@router.get("/student/{student_id}", response_model=StudentResponse)
async def get_student_info(
    student_id: str,
    _: bool = Depends(get_student_access),
    db: Session = Depends(get_db_session)
):
    """Get specific student information"""
    student = db.query(User).filter(
        User.id == student_id,
        User.role == UserRole.STUDENT
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    return student
