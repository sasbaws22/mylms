"""
Module and content-related database models
"""
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON, Text
import enum 
import uuid 
from datetime import datetime
import sqlalchemy.dialects.postgresql as pg




class ContentType(str, enum.Enum):
    """Content type enumeration"""
    VIDEO = "video"
    DOCUMENT = "document"
    QUIZ = "quiz"
    WEBINAR = "webinar"
    INTERACTIVE = "interactive"


class VideoType(str, enum.Enum):
    """Video type enumeration"""
    UPLOADED = "uploaded"
    YOUTUBE = "youtube"
    VIMEO = "vimeo"
    STREAMING = "streaming"


class Module(SQLModel, table=True):
    """Module model""" 
    __tablename__ = "module"

    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )    
    # Foreign key
    course_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="course.id",default=None)
    
    # Module details
    title: str = Field(nullable=False, max_length=200)
    description: Optional[str] = Field(default=None, sa_type=Text)
    content_type: ContentType = Field(nullable=False)
    
    # Content references
    content_url: Optional[str] = Field(default=None, max_length=500)
    content_data: Optional[dict] = Field(default=None, sa_type=JSON) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Module properties
    order_index: int = Field(default=0)
    is_mandatory: bool = Field(default=True)
    estimated_duration: int = Field(default=0)  # in minutes 

    
    # Relationships
    course: "Course" = Relationship(back_populates="modules")
    documents: List["Document"] = Relationship(back_populates="module")
    # videos: List["Video"] = Relationship(back_populates="module")
    quizzes: List["Quiz"] = Relationship(back_populates="module")
    # module_progress: List["ModuleProgress"] = Relationship(back_populates="module") 
    learning_analytics: Optional["LearningAnalytics"] = Relationship(
        back_populates="module"
    )
    
    @property
    def has_quiz(self) -> bool:
        """Check if module has a quiz"""
        return len(self.quizzes) > 0
    
    # @property
    # def has_video(self) -> bool:
    #     """Check if module has a video"""
    #     return len(self.videos) > 0
    
    @property
    def has_documents(self) -> bool:
        """Check if module has documents"""
        return len(self.documents) > 0


class Document(SQLModel, table=True):
    """Document model""" 
    __tablename__ = "document"

    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )    
    # Foreign key
    module_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="module.id",default=None)
    
    # Document details
    title: str = Field(nullable=False, max_length=200)
    file_path: str = Field(nullable=False, max_length=500)
    file_type: str = Field(nullable=False, max_length=10)  # PDF, PPT, DOCX, etc.
    file_size: int = Field(default=0)  # in bytes 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Document properties
    download_count: int = Field(default=0)
    is_downloadable: bool = Field(default=True)
    
    # Relationships
    module: Module = Relationship(back_populates="documents")
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in MB"""
        return self.file_size / (1024 * 1024)


# class Video(SQLModel, table=True):
#     """Video model""" 
#     __tablename__ = "video"
#     id  : uuid.UUID = Field(
#         sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
#     )    
#     # Foreign key
#     module_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="module.id",default=None) 
    
#     # Video details
#     title: str = Field(nullable=False, max_length=200)
#     video_url: str = Field(nullable=False, max_length=500)
#     duration: int = Field(default=0)  # in seconds 
#     thumbnail_url: Optional[str] = Field(default=None, max_length=500)
    
#     # Video properties
#     video_type: VideoType = Field(default=VideoType.UPLOADED)
#     quality_options: List[str] = Field(default_factory=list, sa_type=JSON)
#     subtitles_url: Optional[str] = Field(default=None, max_length=500) 
#     created_at: datetime = Field(default_factory=datetime.now)
#     updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
#     # Relationships
#     module: Module = Relationship(back_populates="videos")
#     # content_progress: List["ContentProgress"] = Relationship(back_populates="video")
    
#     @property
#     def duration_formatted(self) -> str:
#         """Get formatted duration (HH:MM:SS)"""
#         hours = self.duration // 3600
#         minutes = (self.duration % 3600) // 60
#         seconds = self.duration % 60
        
#         if hours > 0:
#             return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
#         else:
#             return f"{minutes:02d}:{seconds:02d}"


# Import other models to avoid circular imports
from app.models.models.course import Course
from app.models.models.quiz import Quiz
# from app.models.models.progress import ModuleProgress, ContentProgress 
from app.models.models.analytics import LearningAnalytics

