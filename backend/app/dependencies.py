from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db_session
from app.config.firebase import verify_firebase_token
from app.models.user import User, UserRole
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
) -> User:
    """Dependency to get current authenticated user"""
    try:
        token = credentials.credentials
        decoded_token = verify_firebase_token(token)
        
        user = db.query(User).filter(User.firebase_uid == decoded_token['uid']).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
            
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure user is an admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def get_teacher_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure user is a teacher"""
    if not current_user.is_teacher and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher privileges required"
        )
    return current_user

async def get_guardian_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure user is a guardian"""
    if not current_user.is_guardian and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guardian privileges required"
        )
    return current_user

def get_student_access(student_id: str, current_user: User = Depends(get_current_user)) -> bool:
    """Check if current user has access to student data"""
    if not current_user.can_view_student(student_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this student's data"
        )
    return True

def get_content_upload_permission(current_user: User = Depends(get_current_user)) -> bool:
    """Check if current user can upload content"""
    if not current_user.can_upload_content():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload content"
        )
    return True

def get_user_management_permission(current_user: User = Depends(get_current_user)) -> bool:
    """Check if current user can manage users"""
    if not current_user.can_manage_users():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage users"
        )
    return True
