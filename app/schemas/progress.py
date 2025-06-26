"""
Progress tracking schemas
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.base import BaseSchema, TimestampMixin, PaginatedResponse
from app.models.models.progress import ProgressStatus


class UserCourseProgressSchema(BaseSchema):
    """User course progress summary schema"""
    enrollment_id: str
    user_id: str
    course_id: str
    course_title: str
    enrollment_status: str
    progress_percentage: float
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    due_date: Optional[datetime]
    total_modules: int
    completed_modules: int
    total_time_spent: int
    last_accessed: Optional[datetime]


class ModuleProgressSchema(BaseSchema, TimestampMixin):
    """Module progress response schema"""
    id: str
    enrollment_id: str
    module_id: str
    module_title: str
    user_id: str
    status: ProgressStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    time_spent: int
    last_accessed: Optional[datetime]
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.status == ProgressStatus.COMPLETED:
            return 100.0
        elif self.status == ProgressStatus.IN_PROGRESS:
            return 50.0
        else:
            return 0.0
    
    @property
    def time_spent_formatted(self) -> str:
        """Get formatted time spent"""
        hours = self.time_spent // 3600
        minutes = (self.time_spent % 3600) // 60
        seconds = self.time_spent % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


class ContentProgressSchema(BaseSchema, TimestampMixin):
    """Content progress response schema"""
    id: str
    module_progress_id: str
    status: ProgressStatus
    progress_percentage: float
    time_spent: int
    last_accessed: Optional[datetime]


class ProgressUpdateSchema(BaseSchema):
    """Progress update schema for a specific content item"""
    course_id: str = Field(..., description="Course ID")
    module_id: str = Field(..., description="Module ID") 
    content_type: str = Field(..., description="Type of content (e.g., video, quiz, document)")
    status: ProgressStatus = Field(..., description="Progress status")
    progress_percentage: float = Field(0.0, ge=0.0, le=100.0, description="Percentage of content completed")
    time_spent: Optional[int] = Field(None, ge=0, description="Time spent on content in seconds")


class VideoProgressSchema(BaseSchema, TimestampMixin):
    """Video progress response schema"""
    id: str
    user_id: str
    video_id: str
    video_title: str
    watch_time: int
    total_duration: int
    progress_percentage: float
    last_position: int
    completed: bool


class VideoProgressUpdateSchema(BaseSchema):
    """Video progress update schema"""
    current_position: int = Field(..., ge=0, description="Current position in seconds")
    total_duration: int = Field(..., ge=0, description="Total video duration in seconds")


class CourseProgressSchema(BaseSchema):
    """Course progress summary schema"""
    course_id: str
    course_title: str
    enrollment_id: str
    enrollment_status: str
    progress_percentage: float
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    due_date: Optional[datetime]
    total_modules: int
    completed_modules: int
    total_time_spent: int
    last_accessed: Optional[datetime]
    
    @property
    def is_overdue(self) -> bool:
        """Check if course is overdue"""
        if not self.due_date or self.completed_at:
            return False
        return datetime.utcnow() > self.due_date
    
    @property
    def time_spent_formatted(self) -> str:
        """Get formatted time spent"""
        hours = self.total_time_spent // 3600
        minutes = (self.total_time_spent % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"


class LearningDashboardSchema(BaseSchema):
    """Learning dashboard schema"""
    user_id: str
    total_enrollments: int
    completed_courses: int
    in_progress_courses: int
    overdue_courses: int
    total_time_spent: int
    total_points: int
    total_certificates: int
    total_badges: int
    
    # Recent activity
    recent_courses: List[CourseProgressSchema] = []
    upcoming_deadlines: List[CourseProgressSchema] = []
    
    # Statistics
    completion_rate: float = 0.0
    average_score: Optional[float] = None
    streak_days: int = 0
    
    @property
    def time_spent_formatted(self) -> str:
        """Get formatted total time spent"""
        hours = self.total_time_spent // 3600
        minutes = (self.total_time_spent % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"


class ProgressStatsSchema(BaseSchema):
    """Progress statistics schema"""
    total_enrollments: int
    completed_enrollments: int
    in_progress_enrollments: int
    average_completion_time: Optional[float]  # in hours
    completion_rate: float
    most_popular_courses: List[dict]
    completion_trends: List[dict]  # Monthly completion data


class LearningPathSchema(BaseSchema):
    """Learning path schema"""
    user_id: str
    recommended_courses: List[dict]
    skill_gaps: List[str]
    next_steps: List[str]
    estimated_completion_time: int  # in hours


# Paginated response types
PaginatedUserCourseProgressResponse = PaginatedResponse[UserCourseProgressSchema]
PaginatedModuleProgressResponse = PaginatedResponse[ModuleProgressSchema]
PaginatedVideoProgressResponse = PaginatedResponse[VideoProgressSchema]
PaginatedCourseProgressResponse = PaginatedResponse[CourseProgressSchema]


