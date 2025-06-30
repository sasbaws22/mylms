"""
User-related database models
"""
from typing import Optional, List
from datetime import datetime, date 
import uuid 
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import Column, Text
from sqlmodel import Field, Relationship,SQLModel


class UserRole:
    """Enumeration for user roles"""
    ADMIN = "admin"
    EMPLOYEE = "employee"
    HR = "hr"
    RESOURCE_PERSONNEL = "resource_personnel" 


class User(SQLModel, table=True):
    """User model"""  
    __tablename__ = "users"
    
    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    ) 
    email: str = Field(..., unique=True, index=True, max_length=255)
    username: str = Field(..., unique=True, index=True, max_length=50)
    password_hash: str = Field(..., max_length=255)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    phone: Optional[str] = Field(None, max_length=20) 
    role: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(None, max_length=500)
    
    # Basic user status fields
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    last_login: Optional[datetime] = None
    
    # For password reset and email verification
    verification_token: Optional[str] = Field(None, max_length=255)
    reset_token: Optional[str] = Field(None, max_length=255)
    reset_token_expires: Optional[datetime] = None 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}) 


    courses:List ["Course"] = Relationship(back_populates="users") 
    # module_progress:List ["ModuleProgress"] = Relationship(back_populates="users") 
    certificates:List ["Certificate"] = Relationship(back_populates="users") 
    user_badges:List ["UserBadge"] = Relationship(back_populates="users") 
    user_points:List ["UserPoints"] = Relationship(back_populates="users")

    enrollment: List["Enrollment"] = Relationship(back_populates="users",sa_relationship_kwargs={"foreign_keys": "[Enrollment.user_id]"}) 
    assigned_by_enrollment: "Enrollment" = Relationship(back_populates="assigned_by_user", sa_relationship_kwargs={"foreign_keys": "[Enrollment.assigned_by]"})
    content_review: List["ContentReview"] = Relationship(back_populates="submitter",sa_relationship_kwargs={"foreign_keys": "[ContentReview.submitter_id]"})
    reviewer_content_review: List["ContentReview"] = Relationship(back_populates="users",sa_relationship_kwargs={"foreign_keys": "[ContentReview.reviewer_id]"})
    quiz_attempts: List["QuizAttempt"] = Relationship(back_populates="users") 
    webinars:List[ "Webinar"] = Relationship(back_populates="users") 
    webinar_registration: List["WebinarRegistration"] = Relationship(back_populates="users") 
    chat_message: "ChatMessage" = Relationship(back_populates="users", sa_relationship_kwargs={"foreign_keys": "[ChatMessage.user_id]"}) 
    chat_message_answerer: "ChatMessage" = Relationship(back_populates="answerer", sa_relationship_kwargs={"foreign_keys": "[ChatMessage.answered_by]"})
    notification: "Notification" = Relationship(back_populates="users") 
    notification_preference: "NotificationPreferences" = Relationship(back_populates="users") 
    user_sessions: "UserSession" = Relationship(back_populates="users") 
    learning_analytics: "LearningAnalytics" = Relationship(back_populates="users") 
    audit_logs: Optional["AuditLog"] = Relationship(back_populates="users")
    content_versions: List["ContentVersion"] = Relationship(back_populates="users")
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "username": "johndoe",
                "password": "SecurePassword123!",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
            }
        }

# Import other models to avoid circular imports
from app.models.models.user import User
from app.models.models.course import Enrollment,Course
from app.models.models.quiz import QuizAttempt 
from app.models.models.review import ContentReview, ContentVersion
# from app.models.models.progress import ModuleProgress
from app.models.models.certificate import Certificate,UserBadge,UserPoints 
from app.models.models.webinar import Webinar,WebinarRegistration,ChatMessage 
from app.models.models.notification import Notification 
from app.models.models.notification import NotificationPreferences 
from app.models.models.analytics import UserSession 
from app.models.models.analytics import LearningAnalytics 
from app.models.models.AuditLog import AuditLog

