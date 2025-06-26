"""
Schemas package - Pydantic schemas for API requests and responses
"""

# Base schemas
from app.schemas.base import (
    BaseSchema, TimestampMixin, PaginationParams, PaginatedResponse,
    MessageResponse, ErrorResponse, HealthCheckResponse, SearchParams, StatusEnum
)

# Authentication schemas
from app.schemas.auth import (
    LoginSchema, TokenResponseSchema, RefreshTokenSchema, UserRegistrationSchema,
    ForgotPasswordSchema, ResetPasswordSchema, ChangePasswordSchema,
    UserResponseSchema, UserProfileSchema, UserUpdateSchema, UserCreateSchema
    
)

# User management schemas
from app.schemas.user import (
    UserListParams, UserSummarySchema, UserDetailSchema, UserStatsSchema,
    PaginatedUsersResponse
)

# Course management schemas
from app.schemas.course import (
    CategorySchema, CategoryCreateSchema, CategoryUpdateSchema,
    CourseListParams, CourseSummarySchema, CourseCreateSchema, CourseUpdateSchema,
    CourseDetailSchema, CourseStatsSchema, EnrollmentSchema, EnrollmentCreateSchema,
    EnrollmentUpdateSchema, EnrollmentListParams, BulkEnrollmentSchema,
    PaginatedCoursesResponse, PaginatedCategoriesResponse, PaginatedEnrollmentsResponse
)

# Module and content schemas
from app.schemas.module import (
    ModuleCreateSchema, ModuleUpdateSchema, ModuleResponseSchema, ModuleDetailSchema,
    DocumentCreateSchema, DocumentSchema, VideoCreateSchema, VideoUpdateSchema,
    VideoSchema, VideoProgressUpdateSchema, FileUploadResponseSchema,
    PaginatedModulesResponse, PaginatedDocumentsResponse, PaginatedVideosResponse
)

# Quiz and assessment schemas
from app.schemas.quiz import (
    QuestionOptionCreateSchema, QuestionOptionSchema, QuestionCreateSchema,
    QuestionUpdateSchema, QuestionSchema, QuizCreateSchema, QuizUpdateSchema,
    QuizSummarySchema, QuizDetailSchema, QuizAttemptStartSchema, QuizResponseSchema,
    QuizSubmissionSchema, QuizResultSchema, QuizResultDetailSchema,
    QuizResponseDetailSchema, QuizAttemptSchema,
    PaginatedQuizzesResponse, PaginatedQuizAttemptsResponse
)

# Progress tracking schemas
from app.schemas.progress import (
    ModuleProgressSchema,VideoProgressSchema,
    VideoProgressUpdateSchema, CourseProgressSchema, LearningDashboardSchema,
    ProgressStatsSchema, LearningPathSchema,
    PaginatedModuleProgressResponse, PaginatedVideoProgressResponse,
    PaginatedCourseProgressResponse
)

# Webinar and communication schemas
from app.schemas.webinar import (
    WebinarCreateSchema, WebinarUpdateSchema, WebinarListParams,
    WebinarRegistrationSchema,
    ChatMessageCreateSchema, ChatMessageSchema,
    ChatMessageAnswerSchema, WebinarStatsSchema, WebinarCalendarSchema,
    PaginatedWebinarsResponse, PaginatedWebinarRegistrationsResponse,
    PaginatedChatMessagesResponse
)

# Notification schemas
from app.schemas.notification import (
    NotificationCreate, BulkNotificationCreateSchema, NotificationListParams,
    NotificationSchema, NotificationPreferencesSchema, NotificationPreferencesUpdateSchema,
    NotificationStatsSchema, NotificationMarkReadSchema, NotificationTemplateSchema,
    PaginatedNotificationsResponse
)

# Analytics and reporting schemas
from app.schemas.analytics import (
    AnalyticsDateRangeParams, LearningAnalyticsCreateSchema, LearningAnalyticsSchema,
    UserAnalyticsSchema, CourseAnalyticsSchema, SystemAnalyticsSchema,
    DepartmentAnalyticsSchema, LearningTrendSchema, EngagementMetricsSchema,
    ReportGenerationSchema, ReportSchema, DashboardMetricsSchema,
    ExportRequestSchema, ExportSchema
)

# Export all schemas
__all__ = [
    # Base schemas
    "BaseSchema", "TimestampMixin", "PaginationParams", "PaginatedResponse",
    "MessageResponse", "ErrorResponse", "HealthCheckResponse", "SearchParams", "StatusEnum",
    
    # Authentication schemas
    "LoginSchema", "TokenResponseSchema", "RefreshTokenSchema", "UserRegistrationSchema",
    "ForgotPasswordSchema", "ResetPasswordSchema", "ChangePasswordSchema",
    "UserResponseSchema", "UserProfileSchema", "UserUpdateSchema", "UserCreateSchema",
    "RoleSchema", "DepartmentSchema",
    
    # User management schemas
    "UserListParams", "UserSummarySchema", "UserDetailSchema", "UserStatsSchema",
    "DepartmentCreateSchema", "DepartmentUpdateSchema", "RoleCreateSchema", "RoleUpdateSchema",
    "PaginatedUsersResponse", "PaginatedDepartmentsResponse", "PaginatedRolesResponse",
    
    # Course management schemas
    "CategorySchema", "CategoryCreateSchema", "CategoryUpdateSchema",
    "CourseListParams", "CourseSummarySchema", "CourseCreateSchema", "CourseUpdateSchema",
    "CourseDetailSchema", "CourseStatsSchema", "EnrollmentSchema", "EnrollmentCreateSchema",
    "EnrollmentUpdateSchema", "EnrollmentListParams", "BulkEnrollmentSchema",
    "PaginatedCoursesResponse", "PaginatedCategoriesResponse", "PaginatedEnrollmentsResponse",
    
    # Module and content schemas
    "ModuleCreateSchema", "ModuleUpdateSchema", "ModuleResponseSchema", "ModuleDetailSchema",
    "DocumentCreateSchema", "DocumentSchema", "VideoCreateSchema", "VideoUpdateSchema",
    "VideoSchema", "VideoProgressUpdateSchema", "FileUploadResponseSchema",
    "PaginatedModulesResponse", "PaginatedDocumentsResponse", "PaginatedVideosResponse",
    
    # Quiz and assessment schemas
    "QuestionOptionCreateSchema", "QuestionOptionSchema", "QuestionCreateSchema",
    "QuestionUpdateSchema", "QuestionSchema", "QuizCreateSchema", "QuizUpdateSchema",
    "QuizSummarySchema", "QuizDetailSchema", "QuizAttemptStartSchema", "QuizResponseSchema",
    "QuizSubmissionSchema", "QuizResultSchema", "QuizResultDetailSchema",
    "QuizResponseDetailSchema", "QuizAttemptSchema",
    "PaginatedQuizzesResponse", "PaginatedQuizAttemptsResponse",
    
    # Progress tracking schemas
    "ModuleProgressSchema", "ModuleProgressUpdateSchema", "VideoProgressSchema",
    "VideoProgressUpdateSchema", "CourseProgressSchema", "LearningDashboardSchema",
    "ProgressStatsSchema", "LearningPathSchema",
    "PaginatedModuleProgressResponse", "PaginatedVideoProgressResponse",
    "PaginatedCourseProgressResponse",
    
    # Webinar and communication schemas
    "WebinarCreateSchema", "WebinarUpdateSchema", "WebinarListParams",
    "WebinarSummarySchema", "WebinarDetailSchema", "WebinarRegistrationSchema",
    "WebinarFeedbackSchema", "ChatMessageCreateSchema", "ChatMessageSchema",
    "ChatMessageAnswerSchema", "WebinarStatsSchema", "WebinarCalendarSchema",
    "PaginatedWebinarsResponse", "PaginatedWebinarRegistrationsResponse",
    "PaginatedChatMessagesResponse",
    
    # Notification schemas
    "NotificationCreateSchema", "BulkNotificationCreateSchema", "NotificationListParams",
    "NotificationSchema", "NotificationPreferencesSchema", "NotificationPreferencesUpdateSchema",
    "NotificationStatsSchema", "NotificationMarkReadSchema", "NotificationTemplateSchema",
    "PaginatedNotificationsResponse",
    
    # Analytics and reporting schemas
    "AnalyticsDateRangeParams", "LearningAnalyticsCreateSchema", "LearningAnalyticsSchema",
    "UserAnalyticsSchema", "CourseAnalyticsSchema", "SystemAnalyticsSchema",
    "DepartmentAnalyticsSchema", "LearningTrendSchema", "EngagementMetricsSchema",
    "ReportGenerationSchema", "ReportSchema", "DashboardMetricsSchema",
    "ExportRequestSchema", "ExportSchema",
]

