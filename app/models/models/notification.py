"""
Notification database models
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text
import enum 
import uuid 
import sqlalchemy.dialects.postgresql as pg




class NotificationType(str, enum.Enum):
    """Notification type enumeration"""
    ASSIGNMENT = "assignment"
    REMINDER = "reminder"
    ACHIEVEMENT = "achievement"
    ANNOUNCEMENT = "announcement"
    WEBINAR = "webinar"


class NotificationPriority(str, enum.Enum):
    """Notification priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(SQLModel, table=True):
    """Notification model""" 
    __tablename__ = "notification" 

    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )      
    # Foreign key
    user_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="users.id",default=None)
    
    # Notification details
    title: str = Field(nullable=False, max_length=200)
    message: str = Field(nullable=False, sa_type=Text)
    notification_type: NotificationType = Field(nullable=False)
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM)
    
    # Status
    is_read: bool = Field(default=False)
    
    # Optional action
    action_url: Optional[str] = Field(default=None, max_length=500)
    
    # Scheduling
    scheduled_for: Optional[datetime] = Field(default=None)
    sent_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    # Relationships
    users: "User" = Relationship(back_populates="notification")
    
    @property
    def is_sent(self) -> bool:
        """Check if notification has been sent"""
        return self.sent_at is not None
    
    @property
    def is_scheduled(self) -> bool:
        """Check if notification is scheduled for future"""
        return self.scheduled_for is not None and self.scheduled_for > datetime.utcnow()


class NotificationPreferences(SQLModel, table=True):
    """User notification preferences model""" 
    __tablename__ = "notification_preference"
    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )    
    # Foreign key
    user_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="users.id",default=None)
    
    # Channel preferences
    email_enabled: bool = Field(default=True)
    sms_enabled: bool = Field(default=False)
    push_enabled: bool = Field(default=True)
    
    # Type preferences
    assignment_notifications: bool = Field(default=True)
    reminder_notifications: bool = Field(default=True)
    achievement_notifications: bool = Field(default=True)
    webinar_notifications: bool = Field(default=True) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    users: "User" = Relationship(back_populates="notification_preference",sa_relationship_kwargs={"foreign_keys": "[NotificationPreferences.user_id]"})


# Import other models to avoid circular imports
from app.models.models.user import User

