"""
Analytics and system database models
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON, Text
import enum 
import uuid 
import sqlalchemy.dialects.postgresql as pg



class ActionType(str, enum.Enum):
    """Action type enumeration for analytics"""
    VIEW = "view"
    START = "start"
    COMPLETE = "complete"
    PAUSE = "pause"
    RESUME = "resume"
    DOWNLOAD = "download"


class UserSession(SQLModel, table=True): 
    __tablename__ = "user_sessions"
    """User session model for tracking user activity""" 
    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
        
    # Foreign key
    user_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="users.id",default=None)
    
    # Session details
    session_start: datetime = Field(nullable=False)
    session_end: Optional[datetime] = Field(default=None)
    ip_address: Optional[str] = Field(default=None, max_length=45)  # IPv6 compatible
    user_agent: Optional[str] = Field(default=None, max_length=500)
    
    # Activity tracking
    pages_visited: List[str] = Field(default_factory=list, sa_type=JSON)
    actions_performed: List[dict] = Field(default_factory=list, sa_type=JSON)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    users: "User" = Relationship(back_populates="user_sessions")
    learning_analytics: List["LearningAnalytics"] = Relationship(back_populates="user_sessions")
    
    @property
    def duration(self) -> Optional[int]:
        """Get session duration in seconds"""
        if not self.session_end:
            return None
        return int((self.session_end - self.session_start).total_seconds())
    
    @property
    def is_active(self) -> bool:
        """Check if session is still active"""
        return self.session_end is None


class LearningAnalytics(SQLModel, table=True): 
    __tablename__ = "learning_analytics"
    """Learning analytics model for tracking learning activities""" 
    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
        
    # Foreign keys
    user_id:Optional[uuid.UUID] =  Field( nullable=True, foreign_key="users.id",default=None)
    course_id:Optional[uuid.UUID] =  Field( nullable=True, foreign_key="course.id",default=None)
    module_id:Optional[uuid.UUID] =  Field( nullable=True, foreign_key="module.id",default=None)
    session_id:Optional[uuid.UUID] =  Field( nullable=True, foreign_key="user_sessions.id",default=None)
    
    # Activity details
    action_type: ActionType = Field(nullable=False)
    action_data: Optional[dict] = Field(default=None, sa_type=JSON)
    timestamp: datetime = Field(default_factory=datetime.now) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    users: "User" = Relationship(back_populates="learning_analytics")
    course: Optional["Course"] = Relationship(
        back_populates="learning_analytics"
    )
    module: Optional["Module"] = Relationship(
        back_populates="learning_analytics"
    )
    user_sessions: Optional[UserSession] = Relationship(back_populates="learning_analytics")


class SystemSettings(SQLModel, table=True): 
    __tablename__ = "system_settings"
    """System settings model"""
    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )    
    # Setting details
    setting_key: str = Field(unique=True, nullable=False, max_length=100)
    setting_value: dict = Field(nullable=False, sa_type=JSON)
    description: Optional[str] = Field(default=None, max_length=255)
    is_public: bool = Field(default=False)  # Whether setting can be read by non-admins 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})


class AuditLog(SQLModel, table=True): 
    __tablename__ = "audit_log"
    """Audit log model for tracking system changes"""
    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )   
    # User and action
    user_id:Optional[uuid.UUID] =  Field( nullable=True, foreign_key="users.id",default=None)
    action: str = Field(nullable=False, max_length=100)
    
    # Resource details
    resource_type: str = Field(nullable=False, max_length=50)
    resource_id: Optional[str] = Field(default=None, max_length=50)
    
    # Change tracking
    old_values: Optional[dict] = Field(default=None, sa_type=JSON)
    new_values: Optional[dict] = Field(default=None, sa_type=JSON)
    
    # Request details
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    timestamp: datetime = Field(default_factory=datetime.utcnow) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    users: Optional["User"] = Relationship(back_populates="audit_log")


# Import other models to avoid circular imports
from app.models.models.user import User
from app.models.models.course import Course
from app.models.models.module import Module

