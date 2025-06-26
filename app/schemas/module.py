"""
Module and content schemas
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.base import BaseSchema, TimestampMixin, PaginatedResponse
from app.models.models.module import ContentType, VideoType


class ModuleCreateSchema(BaseSchema):
    """Module creation schema"""
    title: str = Field(..., min_length=1, max_length=200, description="Module title")
    description: Optional[str] = Field(None, description="Module description")
    content_type: ContentType = Field(..., description="Content type")
    content_url: Optional[str] = Field(None, max_length=500, description="Content URL")
    content_data: Optional[Dict[str, Any]] = Field(None, description="Content configuration data")
    order_index: int = Field(default=0, ge=0, description="Order index within course")
    is_mandatory: bool = Field(default=True, description="Is module mandatory")
    estimated_duration: int = Field(default=0, ge=0, description="Estimated duration in minutes")


class ModuleUpdateSchema(BaseSchema):
    """Module update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None)
    content_type: Optional[ContentType] = Field(None)
    content_url: Optional[str] = Field(None, max_length=500)
    content_data: Optional[Dict[str, Any]] = Field(None)
    order_index: Optional[int] = Field(None, ge=0)
    is_mandatory: Optional[bool] = Field(None)
    estimated_duration: Optional[int] = Field(None, ge=0)


class ModuleResponseSchema(BaseSchema, TimestampMixin):
    """Module response schema"""
    id: str
    course_id: str
    title: str
    description: Optional[str]
    content_type: ContentType
    content_url: Optional[str]
    content_data: Optional[Dict[str, Any]]
    order_index: int
    is_mandatory: bool
    estimated_duration: int
    
    # Computed properties
    has_quiz: bool = False
    has_video: bool = False
    has_documents: bool = False


class ModuleDetailSchema(BaseSchema, TimestampMixin):
    """Detailed module schema with related content"""
    id: str
    course_id: str
    course_title: str
    title: str
    description: Optional[str]
    content_type: ContentType
    content_url: Optional[str]
    content_data: Optional[Dict[str, Any]]
    order_index: int
    is_mandatory: bool
    estimated_duration: int


class DocumentCreateSchema(BaseSchema):
    """Document creation schema"""
    title: str = Field(..., min_length=1, max_length=200, description="Document title")
    file_type: str = Field(..., max_length=10, description="File type (PDF, PPT, etc.)")
    is_downloadable: bool = Field(default=True, description="Is document downloadable")


class DocumentSchema(BaseSchema, TimestampMixin):
    """Document response schema"""
    id: str
    module_id: str
    title: str
    file_path: str
    file_type: str
    file_size: int
    download_count: int
    is_downloadable: bool
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in MB"""
        return self.file_size / (1024 * 1024)


class VideoCreateSchema(BaseSchema):
    """Video creation schema"""
    title: str = Field(..., min_length=1, max_length=200, description="Video title")
    video_url: str = Field(..., max_length=500, description="Video URL")
    duration: int = Field(default=0, ge=0, description="Video duration in seconds")
    thumbnail_url: Optional[str] = Field(None, max_length=500, description="Thumbnail URL")
    video_type: VideoType = Field(default=VideoType.UPLOADED, description="Video type")
    quality_options: List[str] = Field(default_factory=list, description="Available quality options")
    subtitles_url: Optional[str] = Field(None, max_length=500, description="Subtitles URL")


class VideoUpdateSchema(BaseSchema):
    """Video update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    video_url: Optional[str] = Field(None, max_length=500)
    duration: Optional[int] = Field(None, ge=0)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    video_type: Optional[VideoType] = Field(None)
    quality_options: Optional[List[str]] = Field(None)
    subtitles_url: Optional[str] = Field(None, max_length=500)


class VideoSchema(BaseSchema, TimestampMixin):
    """Video response schema"""
    id: str
    module_id: str
    title: str
    video_url: str
    duration: int
    thumbnail_url: Optional[str]
    video_type: VideoType
    quality_options: List[str]
    subtitles_url: Optional[str]
    
    @property
    def duration_formatted(self) -> str:
        """Get formatted duration (HH:MM:SS)"""
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


class VideoProgressUpdateSchema(BaseSchema):
    """Video progress update schema"""
    current_position: int = Field(..., ge=0, description="Current position in seconds")
    total_duration: int = Field(..., ge=0, description="Total video duration in seconds")


class FileUploadResponseSchema(BaseSchema):
    """File upload response schema"""
    file_id: str
    filename: str
    file_path: str
    file_size: int
    file_type: str
    upload_url: Optional[str] = None


# Import quiz schema for forward reference
from app.schemas.quiz import QuizSummarySchema
from app.schemas.progress import ModuleProgressSchema

# Paginated response types
PaginatedModulesResponse = PaginatedResponse[ModuleResponseSchema]
PaginatedDocumentsResponse = PaginatedResponse[DocumentSchema]
PaginatedVideosResponse = PaginatedResponse[VideoSchema]

