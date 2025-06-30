"""
Progress tracking database models
"""
from datetime import datetime
from typing import Optional,List
from sqlmodel import SQLModel, Field, Relationship
import enum 
import uuid 
import sqlalchemy.dialects.postgresql as pg 
from sqlalchemy import Column, Text


class ContentType(str, enum.Enum):
    """Content type enumeration"""
    VIDEO = "video"
    DOCUMENT = "document"
    QUIZ = "quiz"


class ProgressStatus(str, enum.Enum):
    """Progress status enumeration"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# class ModuleProgress(SQLModel, table=True):
#     """Module progress tracking model""" 
#     __tablename__ = "module_progress"  

#     id  : uuid.UUID = Field(
#         sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
#     )  
        
#     # Foreign keys
#     enrollment_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="enrollment.id",default=None)
#     module_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="module.id",default=None)
#     user_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="users.id",default=None)
    
#     # Progress details
#     status: ProgressStatus = Field(default=ProgressStatus.NOT_STARTED)
#     started_at: Optional[datetime] = Field(default=None)
#     completed_at: Optional[datetime] = Field(default=None)
#     time_spent: int = Field(default=0)  # in seconds
#     last_accessed: Optional[datetime] = Field(default=None) 
#     created_at: datetime = Field(default_factory=datetime.now)
#     updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
#     # Relationships
#     enrollment: "Enrollment" = Relationship(back_populates="module_progress")
#     module: "Module" = Relationship(back_populates="module_progress")
#     users: "User" = Relationship(back_populates="module_progress")
#     content_progress: List["ContentProgress"] = Relationship(back_populates="module_progress")
    
    # @property
    # def progress_percentage(self) -> float:
    #     """Calculate progress percentage"""
    #     if self.status == ProgressStatus.COMPLETED:
    #         return 100.0
    #     elif self.status == ProgressStatus.IN_PROGRESS:
    #         # This could be calculated based on video watch time, quiz completion, etc.
    #         return 50.0
    #     else:
    #         return 0.0
    
    # @property
    # def time_spent_formatted(self) -> str:
    #     """Get formatted time spent"""
    #     hours = self.time_spent // 3600
    #     minutes = (self.time_spent % 3600) // 60
    #     seconds = self.time_spent % 60
        
    #     if hours > 0:
    #         return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    #     else:
    #         return f"{minutes:02d}:{seconds:02d}"


from app.models.models.course import Enrollment
from app.models.models.module import Module, Video
from app.models.models.user import User




class ContentProgress(SQLModel, table=True):
    """Content progress tracking model"""
    __tablename__ = "content_progress"

    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )

    # Foreign keys
    # module_progress_id: Optional[uuid.UUID] = Field(nullable=True, foreign_key="module_progress.id", default=None) 
    video_id: Optional[uuid.UUID] = Field(nullable=True, foreign_key="video.id", default=None)
    content_type: str = Field(nullable=False) # Type of content (video, document, quiz)

    # Progress details
    status: ProgressStatus = Field(default=ProgressStatus.NOT_STARTED)
    progress_percentage: float = Field(default=0.0)
    time_spent: int = Field(default=0)  # in seconds
    last_accessed: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})

    # Relationships
    # module_progress: ModuleProgress = Relationship(back_populates="content_progress") 
    video : Optional["Video"] = Relationship(back_populates="content_progress", sa_relationship_kwargs={"foreign_keys": "[ContentProgress.video_id]"})


