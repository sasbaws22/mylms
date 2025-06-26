"""
Analytics and reporting schemas
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date

from app.schemas.base import BaseSchema, TimestampMixin, SearchParams
from app.models.models.analytics import ActionType


class AnalyticsDateRangeParams(BaseModel):
    """Date range parameters for analytics"""
    start_date: Optional[date] = Field(None, description="Start date for analytics")
    end_date: Optional[date] = Field(None, description="End date for analytics")
    period: Optional[str] = Field(default="month", pattern="^(day|week|month|quarter|year)$", description="Period grouping")


class LearningAnalyticsCreateSchema(BaseSchema):
    """Learning analytics creation schema"""
    user_id: str = Field(..., description="User ID")
    course_id: Optional[str] = Field(None, description="Course ID")
    module_id: Optional[str] = Field(None, description="Module ID")
    action_type: ActionType = Field(..., description="Action type")
    action_data: Optional[Dict[str, Any]] = Field(None, description="Additional action data")


class LearningAnalyticsSchema(BaseSchema, TimestampMixin):
    """Learning analytics response schema"""
    id: str
    user_id: str
    course_id: Optional[str]
    module_id: Optional[str]
    session_id: Optional[str]
    action_type: ActionType
    action_data: Optional[Dict[str, Any]]
    timestamp: datetime


class UserAnalyticsSchema(BaseSchema):
    """User analytics schema"""
    user_id: str
    user_name: str
    department: Optional[str]
    
    # Learning metrics
    total_enrollments: int
    completed_courses: int
    in_progress_courses: int
    completion_rate: float
    average_score: Optional[float]
    total_time_spent: int  # in minutes
    
    # Activity metrics
    login_count: int
    last_login: Optional[datetime]
    active_days: int
    streak_days: int
    
    # Engagement metrics
    quiz_attempts: int
    webinar_attendance: int
    document_downloads: int
    video_watch_time: int  # in minutes
    
    # Achievements
    total_points: int
    total_certificates: int
    total_badges: int


class CourseAnalyticsSchema(BaseSchema):
    """Course analytics schema"""
    course_id: str
    course_title: str
    category: str
    
    # Enrollment metrics
    total_enrollments: int
    active_enrollments: int
    completed_enrollments: int
    dropped_enrollments: int
    completion_rate: float
    
    # Performance metrics
    average_score: Optional[float]
    average_completion_time: Optional[float]  # in hours
    pass_rate: float
    
    # Engagement metrics
    total_time_spent: int  # in minutes
    average_time_per_user: float  # in minutes
    module_completion_rates: List[Dict[str, Any]]
    
    # Trends
    enrollment_trend: List[Dict[str, Any]]
    completion_trend: List[Dict[str, Any]]


class SystemAnalyticsSchema(BaseSchema):
    """System-wide analytics schema"""
    # User metrics
    total_users: int
    active_users: int
    new_users_this_month: int
    user_growth_rate: float
    
    # Course metrics
    total_courses: int
    published_courses: int
    total_enrollments: int
    total_completions: int
    overall_completion_rate: float
    
    # Content metrics
    total_modules: int
    total_quizzes: int
    total_videos: int
    total_documents: int
    
    # Activity metrics
    daily_active_users: int
    weekly_active_users: int
    monthly_active_users: int
    total_learning_time: int  # in hours
    
    # Popular content
    most_popular_courses: List[Dict[str, Any]]
    most_active_users: List[Dict[str, Any]]
    trending_categories: List[Dict[str, Any]]


class DepartmentAnalyticsSchema(BaseSchema):
    """Department analytics schema"""
    department_id: str
    department_name: str
    
    # User metrics
    total_users: int
    active_users: int
    
    # Learning metrics
    total_enrollments: int
    completed_courses: int
    completion_rate: float
    average_score: Optional[float]
    
    # Time metrics
    total_learning_time: int  # in minutes
    average_time_per_user: float  # in minutes
    
    # Top performers
    top_learners: List[Dict[str, Any]]
    popular_courses: List[Dict[str, Any]]


class LearningTrendSchema(BaseSchema):
    """Learning trend schema"""
    period: str  # Date or period identifier
    enrollments: int
    completions: int
    active_users: int
    total_time_spent: int  # in minutes
    average_score: Optional[float]


class EngagementMetricsSchema(BaseSchema):
    """Engagement metrics schema"""
    user_id: str
    date: date
    
    # Activity metrics
    login_duration: int  # in minutes
    pages_visited: int
    actions_performed: int
    
    # Learning metrics
    modules_accessed: int
    videos_watched: int
    quizzes_taken: int
    documents_downloaded: int
    
    # Engagement score (calculated)
    engagement_score: float


class ReportGenerationSchema(BaseSchema):
    """Report generation request schema"""
    report_type: str = Field(..., pattern="^(user|course|department|system|engagement)$", description="Report type")
    format: str = Field(default="pdf", pattern="^(pdf|csv|xlsx)$", description="Report format")
    date_range: AnalyticsDateRangeParams
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")
    include_charts: bool = Field(default=True, description="Include charts in report")


class ReportSchema(BaseSchema, TimestampMixin):
    """Report response schema"""
    id: str
    report_type: str
    format: str
    status: str  # generating, completed, failed
    file_url: Optional[str]
    generated_by: str
    parameters: Dict[str, Any]
    file_size: Optional[int]  # in bytes


class DashboardMetricsSchema(BaseSchema):
    """Dashboard metrics schema"""
    # Quick stats
    total_users: int
    total_courses: int
    total_enrollments: int
    completion_rate: float
    
    # Recent activity
    new_enrollments_today: int
    completions_today: int
    active_users_today: int
    
    # Trends (last 30 days)
    enrollment_trend: List[LearningTrendSchema]
    completion_trend: List[LearningTrendSchema]
    user_activity_trend: List[LearningTrendSchema]
    
    # Top performers
    top_courses: List[Dict[str, Any]]
    top_learners: List[Dict[str, Any]]
    top_departments: List[Dict[str, Any]]


class ExportRequestSchema(BaseSchema):
    """Data export request schema"""
    data_type: str = Field(..., pattern="^(users|courses|enrollments|analytics|all)$", description="Data type to export")
    format: str = Field(default="csv", pattern="^(csv|xlsx|json)$", description="Export format")
    date_range: Optional[AnalyticsDateRangeParams] = Field(None, description="Date range filter")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")
    include_personal_data: bool = Field(default=False, description="Include personal data (requires admin permission)")


class ExportSchema(BaseSchema, TimestampMixin):
    """Data export response schema"""
    id: str
    data_type: str
    format: str
    status: str  # pending, processing, completed, failed
    file_url: Optional[str]
    file_size: Optional[int]  # in bytes
    record_count: Optional[int]
    requested_by: str
    expires_at: Optional[datetime]

