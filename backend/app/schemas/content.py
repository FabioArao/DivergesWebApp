from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.content import ContentType

class ContentCategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class ContentCategoryCreate(ContentCategoryBase):
    pass

class ContentCategoryResponse(ContentCategoryBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EducationalContentBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    content_type: ContentType
    file_path: str
    file_size: int = Field(..., gt=0)
    mime_type: str
    duration: Optional[int] = Field(None, gt=0)
    category_id: str
    is_published: bool = False

class EducationalContentCreate(EducationalContentBase):
    @validator('duration')
    def validate_duration(cls, v, values):
        if values.get('content_type') == ContentType.VIDEO and v is None:
            raise ValueError("Duration is required for video content")
        return v

class EducationalContentResponse(EducationalContentBase):
    id: str
    uploaded_by: str
    view_count: int
    download_count: int
    created_at: datetime
    updated_at: datetime
    category: Optional[ContentCategoryResponse]

    class Config:
        from_attributes = True

class ContentAccessBase(BaseModel):
    content_id: str
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    completed: bool = False

class ContentAccessCreate(ContentAccessBase):
    pass

class ContentAccessResponse(ContentAccessBase):
    id: str
    user_id: str
    last_accessed: datetime
    created_at: datetime
    updated_at: datetime
    content: Optional[EducationalContentResponse]

    class Config:
        from_attributes = True

class ContentCommentBase(BaseModel):
    content_id: str
    comment: str = Field(..., min_length=1, max_length=1000)

class ContentCommentCreate(ContentCommentBase):
    pass

class ContentCommentResponse(ContentCommentBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ContentUploadRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    content_type: ContentType
    category_id: str
    is_published: bool = False

class ContentFilterParams(BaseModel):
    content_type: Optional[ContentType] = None
    category_id: Optional[str] = None
    is_published: Optional[bool] = None
    min_view_count: Optional[int] = Field(None, ge=0)
    uploaded_by: Optional[str] = None

class ContentProgressUpdateRequest(BaseModel):
    progress: float = Field(..., ge=0.0, le=100.0)
    completed: Optional[bool] = False
