from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.user import User
from datetime import datetime
import enum
import uuid

class ContentType(str, enum.Enum):
    VIDEO = "video"
    DOCUMENT = "document"
    EBOOK = "ebook"

class ContentCategory(Base):
    __tablename__ = "content_categories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    
    # Relationship
    contents = relationship("EducationalContent", back_populates="category")

class EducationalContent(Base):
    __tablename__ = "educational_content"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text)
    content_type = Column(Enum(ContentType), nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    duration = Column(Integer)  # For videos (in seconds)
    
    # Foreign Keys
    category_id = Column(String, ForeignKey('content_categories.id'), nullable=False)
    uploaded_by = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Additional metadata
    is_published = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    
    # Relationships
    category = relationship("ContentCategory", back_populates="contents")
    uploader = relationship("User")
    access_logs = relationship("ContentAccess", back_populates="content")
    comments = relationship("ContentComment", back_populates="content")

class ContentAccess(Base):
    __tablename__ = "content_access"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys
    content_id = Column(String, ForeignKey('educational_content.id'), nullable=False)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Access metadata
    last_accessed = Column(DateTime, default=datetime.utcnow)
    progress = Column(Float, default=0.0)  # Percentage of content viewed/read
    completed = Column(Boolean, default=False)
    
    # Relationships
    content = relationship("EducationalContent", back_populates="access_logs")
    user = relationship("User")

class ContentComment(Base):
    __tablename__ = "content_comments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys
    content_id = Column(String, ForeignKey('educational_content.id'), nullable=False)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Comment details
    comment = Column(Text, nullable=False)
    
    # Relationships
    content = relationship("EducationalContent", back_populates="comments")
    user = relationship("User")

    def to_dict(self):
        """Convert comment to dictionary"""
        return {
            "id": self.id,
            "content_id": self.content_id,
            "user_id": self.user_id,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
