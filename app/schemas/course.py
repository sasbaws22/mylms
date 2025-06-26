"""
Course management schemas
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.base import BaseSchema, TimestampMixin, PaginatedResponse, SearchParams
from app.models.models.course import CourseStatus, DifficultyLevel, EnrollmentStatus


class CategorySchema(BaseSchema, TimestampMixin):
    """Category response schema"""
    id: str
    name: str
    description: Optional[str]
    parent_id: Optional[str]
    color_code: Optional[str]
    total_courses: int = 0


class CategoryCreateSchema(BaseSchema):
    """Category creation schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=255, description="Category description")
    parent_id: Optional[str] = Field(None, description="Parent category ID")
    color_code: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="Hex color code")


class CategoryUpdateSchema(BaseSchema):
    """Category update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    parent_id: Optional[str] = Field(None)
    color_code: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")


class CourseListParams(SearchParams):
    """Course list query parameters"""
    category_id: Optional[str] = Field(None, description="Filter by category")
    difficulty: Optional[DifficultyLevel] = Field(None, description="Filter by difficulty")
    status: Optional[CourseStatus] = Field(None, description="Filter by status")
    creator_id: Optional[str] = Field(None, description="Filter by creator")
    is_mandatory: Optional[bool] = Field(None, description="Filter by mandatory status")


class CourseSummarySchema(BaseSchema):
    """Course summary schema for lists"""
    id: str
    title: str
    description: Optional[str]
    category_name: str
    creator_name: str
    status: CourseStatus
    difficulty_level: DifficultyLevel
    estimated_duration: int
    is_mandatory: bool
    thumbnail_url: Optional[str]
    total_modules: int
    total_enrollments: int
    created_at: datetime


class CourseCreateSchema(BaseSchema):
    """Course creation schema"""
    title: str = Field(..., min_length=1, max_length=200, description="Course title")
    description: Optional[str] = Field(None, description="Course description")
    category_id: str = Field(..., description="Category ID")
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER, description="Difficulty level")
    estimated_duration: int = Field(default=0, ge=0, description="Estimated duration in minutes")
    is_mandatory: bool = Field(default=False, description="Is course mandatory")
    prerequisites: List[str] = Field(default_factory=list, description="List of prerequisite course IDs")
    tags: List[str] = Field(default_factory=list, description="Course tags")
    thumbnail_url: Optional[str] = Field(None, max_length=500, description="Thumbnail URL")


class CourseUpdateSchema(BaseSchema):
    """Course update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None)
    category_id: Optional[str] = Field(None)
    difficulty_level: Optional[DifficultyLevel] = Field(None)
    estimated_duration: Optional[int] = Field(None, ge=0)
    is_mandatory: Optional[bool] = Field(None)
    prerequisites: Optional[List[str]] = Field(None)
    tags: Optional[List[str]] = Field(None)
    thumbnail_url: Optional[str] = Field(None, max_length=500)


class CourseDetailSchema(BaseSchema, TimestampMixin):
    """Detailed course schema"""
    id: str
    title: str
    description: Optional[str]
    category_id: str
    category_name: str
    creator_id: str
    creator_name: str
    status: CourseStatus
    difficulty_level: DifficultyLevel
    estimated_duration: int
    is_mandatory: bool
    prerequisites: List[str]
    tags: List[str]
    thumbnail_url: Optional[str]
    published_at: Optional[datetime]
    
    # Statistics
    total_modules: int
    total_enrollments: int
    completion_rate: float
    average_rating: Optional[float] = None
    user_progress: float = 0.0


class CourseStatsSchema(BaseSchema):
    """Course statistics schema"""
    total_courses: int
    published_courses: int
    draft_courses: int
    courses_by_category: List[dict]
    courses_by_difficulty: List[dict]
    most_popular_courses: List[dict]


class EnrollmentSchema(BaseSchema, TimestampMixin):
    """Enrollment response schema"""
    id: str
    user_id: str
    course_id: str
    enrolled_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    progress_percentage: float
    status: EnrollmentStatus
    assigned_by: Optional[str]
    due_date: Optional[datetime]
    
    # Related data
    user_name: Optional[str]
    course_title: Optional[str]
    
    @property
    def is_overdue(self) -> bool:
        """Check if enrollment is overdue"""
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date and self.status != EnrollmentStatus.COMPLETED


class EnrollmentCreateSchema(BaseSchema):
    """Enrollment creation schema"""
    user_id: str = Field(..., description="User ID to enroll")
    course_id: str = Field(..., description="Course ID")
    due_date: Optional[datetime] = Field(None, description="Due date for completion")


class EnrollmentUpdateSchema(BaseSchema):
    """Enrollment update schema"""
    status: Optional[EnrollmentStatus] = Field(None)
    due_date: Optional[datetime] = Field(None)


class EnrollmentListParams(SearchParams):
    """Enrollment list query parameters"""
    user_id: Optional[str] = Field(None, description="Filter by user")
    course_id: Optional[str] = Field(None, description="Filter by course")
    status: Optional[EnrollmentStatus] = Field(None, description="Filter by status")
    assigned_by: Optional[str] = Field(None, description="Filter by who assigned")


class BulkEnrollmentSchema(BaseSchema):
    """Bulk enrollment schema"""
    user_ids: List[str] = Field(..., min_items=1, description="List of user IDs")
    course_id: str = Field(..., description="Course ID")
    due_date: Optional[datetime] = Field(None, description="Due date for completion")


# Paginated response types
PaginatedCoursesResponse = PaginatedResponse[CourseSummarySchema]
PaginatedCategoriesResponse = PaginatedResponse[CategorySchema]
PaginatedEnrollmentsResponse = PaginatedResponse[EnrollmentSchema]

