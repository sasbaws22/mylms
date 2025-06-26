"""
Content review and approval database models
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text
import enum 
import uuid 
import sqlalchemy.dialects.postgresql as pg



class ReviewStatus(str, enum.Enum):
    """Review status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class ContentTypeEnum(str, enum.Enum):
    """Content type enumeration for reviews"""
    COURSE = "course"
    MODULE = "module"
    QUIZ = "quiz"
    DOCUMENT = "document"
    VIDEO = "video"


class ContentReview(SQLModel, table=True):
    """Content review model""" 
    __tablename__ = "content_review" 

    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    ) 
        
    # Content reference
    course_id: Optional[uuid.UUID] = Field(nullable=False,foreign_key="course.id",default=None) 

    module_id: Optional[uuid.UUID] = Field(nullable=False,foreign_key="module.id",default=None)  
    content_type: ContentTypeEnum = Field(nullable=False)
    
    # Foreign keys
    reviewer_id:Optional[uuid.UUID] = Field( nullable=True,foreign_key="users.id",default=None)
    submitter_id:Optional[uuid.UUID] = Field( nullable=True,foreign_key="users.id",default=None)
    
    # Review details
    status: ReviewStatus = Field(default=ReviewStatus.PENDING)
    review_notes: Optional[str] = Field(default=None, sa_type=Text)
    reviewed_at: Optional[datetime] = Field(default=None) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    users: "User" = Relationship(back_populates="content_review",sa_relationship_kwargs={"foreign_keys": "[ContentReview.reviewer_id]"})
    submitter: "User" = Relationship(back_populates="content_review",sa_relationship_kwargs={"foreign_keys": "[ContentReview.submitter_id]"})
    
    # Dynamic relationship to course (when content_type is COURSE)
    course: Optional["Course"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "and_(ContentReview.course_id == Course.id, ContentReview.content_type == 'course')",
            "foreign_keys": "ContentReview.course_id",
            "uselist": False
        }
    )
    
    @property
    def is_pending(self) -> bool:
        """Check if review is pending"""
        return self.status == ReviewStatus.PENDING
    
    @property
    def is_approved(self) -> bool:
        """Check if review is approved"""
        return self.status == ReviewStatus.APPROVED


class ContentVersion(SQLModel, table=True):
    """Content version model for tracking changes""" 
    __tablename__ = "content_version" 

    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
        
    # Content reference
    content_type: ContentTypeEnum = Field(nullable=False)
    
    # Version details
    version_number: int = Field(nullable=False)
    changes_summary: Optional[str] = Field(default=None, sa_type=Text)
    created_by:Optional[uuid.UUID] = Field( nullable=True, foreign_key="users.id",default=None)
    is_current: bool = Field(default=False) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    users: "User" = Relationship(back_populates="content_versions",sa_relationship_kwargs={"foreign_keys": "[ContentVersion.created_by]"})



# Import other models to avoid circular imports
from app.models.models.user import User
from app.models.models.course import Course
