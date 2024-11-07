from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db_session
from app.dependencies import (
    get_current_user, 
    get_teacher_user, 
    get_student_access
)
from app.models.user import User
from app.models.content import ContentType, ContentCategory, EducationalContent
from app.schemas.content import (
    ContentCategoryCreate, 
    ContentCategoryResponse,
    EducationalContentCreate,
    EducationalContentResponse,
    ContentFilterParams,
    ContentProgressUpdateRequest,
    ContentAccessResponse
)
from app.config.settings import settings
import logging
import os
import uuid
import mimetypes

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/content", tags=["Educational Content"])

@router.post("/categories", response_model=ContentCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_content_category(
    category: ContentCategoryCreate,
    _: User = Depends(get_teacher_user),
    db: Session = Depends(get_db_session)
):
    """Create a new content category"""
    try:
        db_category = ContentCategory(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        logger.error(f"Error creating content category: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/upload", response_model=EducationalContentResponse, status_code=status.HTTP_201_CREATED)
async def upload_content(
    file: UploadFile = File(...),
    content_type: ContentType = File(...),
    title: str = File(...),
    description: Optional[str] = File(None),
    category_id: str = File(...),
    is_published: bool = File(False),
    current_user: User = Depends(get_teacher_user),
    db: Session = Depends(get_db_session)
):
    """Upload educational content"""
    try:
        # Validate file type
        if file.content_type not in settings.allowed_file_types_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type"
            )
        
        # Check file size
        file_size = 0
        file_path = None
        try:
            # Create uploads directory if not exists
            os.makedirs("uploads", exist_ok=True)
            
            # Generate unique filename
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join("uploads", unique_filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                while chunk := await file.read(1024 * 1024):  # Read in 1MB chunks
                    buffer.write(chunk)
                    file_size += len(chunk)
            
            # Check file size against max upload size
            if file_size > settings.MAX_UPLOAD_SIZE:
                os.remove(file_path)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File size exceeds maximum limit"
                )
        except Exception as file_error:
            logger.error(f"File upload error: {str(file_error)}")
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            raise
        
        # Determine duration for video content
        duration = None
        if content_type == ContentType.VIDEO:
            # TODO: Implement video duration extraction using ffprobe or similar
            pass
        
        # Create content record
        content = EducationalContent(
            title=title,
            description=description,
            content_type=content_type,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type,
            duration=duration,
            category_id=category_id,
            uploaded_by=current_user.id,
            is_published=is_published
        )
        
        db.add(content)
        db.commit()
        db.refresh(content)
        
        return content
    
    except Exception as e:
        logger.error(f"Content upload error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[EducationalContentResponse])
async def list_content(
    filters: ContentFilterParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """List educational content with optional filtering"""
    query = db.query(EducationalContent)
    
    # Apply filters
    if filters.content_type:
        query = query.filter(EducationalContent.content_type == filters.content_type)
    
    if filters.category_id:
        query = query.filter(EducationalContent.category_id == filters.category_id)
    
    if filters.is_published is not None:
        query = query.filter(EducationalContent.is_published == filters.is_published)
    
    if filters.min_view_count is not None:
        query = query.filter(EducationalContent.view_count >= filters.min_view_count)
    
    if filters.uploaded_by:
        query = query.filter(EducationalContent.uploaded_by == filters.uploaded_by)
    
    # Ensure non-admin users only see published content
    if not current_user.is_admin:
        query = query.filter(EducationalContent.is_published == True)
    
    return query.all()

@router.get("/{content_id}", response_model=EducationalContentResponse)
async def get_content(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get specific content by ID"""
    content = db.query(EducationalContent).filter(EducationalContent.id == content_id).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Check if content is published or user is admin/uploader
    if not content.is_published and not (current_user.is_admin or content.uploaded_by == current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this content"
        )
    
    return content

@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: str,
    current_user: User = Depends(get_teacher_user),
    db: Session = Depends(get_db_session)
):
    """Delete educational content"""
    content = db.query(EducationalContent).filter(EducationalContent.id == content_id).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Ensure only admin or original uploader can delete
    if not (current_user.is_admin or content.uploaded_by == current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this content"
        )
    
    try:
        # Remove physical file
        if os.path.exists(content.file_path):
            os.remove(content.file_path)
        
        # Delete database record
        db.delete(content)
        db.commit()
    except Exception as e:
        logger.error(f"Content deletion error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete content"
        )
