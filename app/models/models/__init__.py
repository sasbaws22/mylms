"""
Database models package
"""

# Import all models to ensure they are registered with SQLModel
from app.models.models.user import User
from app.models.models.course import Course, Category, Enrollment, CourseStatus, DifficultyLevel, EnrollmentStatus
from app.models.models.module import Module, Document,ContentType, VideoType
from app.models.models.module import Video
from app.models.models.quiz import Quiz, Question, QuestionOption, QuizAttempt, QuizResponse, QuestionType
from app.models.models.progress import ProgressStatus
from app.models.models.progress import ModuleProgress
from app.models.models.webinar import Webinar, WebinarRegistration, ChatMessage, WebinarStatus, MessageType
from app.models.models.notification import Notification, NotificationPreferences, NotificationType, NotificationPriority
from app.models.models.certificate import Certificate, Badge, UserBadge, UserPoints, CertificateType, BadgeType, PointsSource
from app.models.models.review import ContentReview, ContentVersion, ReviewStatus, ContentTypeEnum
from app.models.models.analytics import UserSession, LearningAnalytics, SystemSettings,ActionType 
from app.models.models.AuditLog import AuditLog

# Export all models
__all__ = [
    # Base
    "BaseModel",
    
    # User models
    "User", "Role", "Department", "UserRole",
    
    # Course models
    "Course", "Category", "Enrollment", "CourseStatus", "DifficultyLevel", "EnrollmentStatus",
    
    # Module models
    "Module", "Document", "Video", "ContentType", "VideoType",
    
    # Quiz models
    "Quiz", "Question", "QuestionOption", "QuizAttempt", "QuizResponse", "QuestionType",
    
    # Progress models
    "ModuleProgress", "VideoProgress", "ProgressStatus",
    
    # Webinar models
    "Webinar", "WebinarRegistration", "ChatMessage", "WebinarStatus", "MessageType",
    
    # Notification models
    "Notification", "NotificationPreferences", "NotificationType", "NotificationPriority",
    
    # Certificate and gamification models
    "Certificate", "Badge", "UserBadge", "UserPoints", "CertificateType", "BadgeType", "PointsSource",
    
    # Review models
    "ContentReview", "ContentVersion", "ReviewStatus", "ContentTypeEnum",
    
    # Analytics models
    "UserSession", "LearningAnalytics", "SystemSettings", "AuditLog", "ActionType",
]

