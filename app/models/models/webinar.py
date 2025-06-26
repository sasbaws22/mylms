"""
Webinar and communication database models
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text
import enum 
import uuid 
import sqlalchemy.dialects.postgresql as pg


class WebinarStatus(str, enum.Enum):
    """Webinar status enumeration"""
    SCHEDULED = "scheduled"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MessageType(str, enum.Enum):
    """Message type enumeration"""
    TEXT = "text"
    QUESTION = "question"
    ANNOUNCEMENT = "announcement"


class Webinar(SQLModel, table=True):
    """Webinar model"""  
    __tablename__ = "webinar"
    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    ) 
        
    # Webinar details
    title: str = Field(nullable=False, max_length=200)
    description: Optional[str] = Field(default=None, sa_type=Text)
    
    # Foreign key
    presenter_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="users.id",default=None)
    
    # Scheduling
    scheduled_at: datetime = Field(nullable=False)
    duration: int = Field(default=60)  # in minutes
    
    # Meeting details
    meeting_url: Optional[str] = Field(default=None, max_length=500)
    meeting_id: Optional[str] = Field(default=None, max_length=100)
    meeting_password: Optional[str] = Field(default=None, max_length=50)
    max_participants: Optional[int] = Field(default=None)
    
    # Status and recording
    status: WebinarStatus = Field(default=WebinarStatus.SCHEDULED)
    recording_url: Optional[str] = Field(default=None, max_length=500)
    is_recorded: bool = Field(default=False) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    users: "User" = Relationship(back_populates="webinars")
    webinar_registration: List["WebinarRegistration"] = Relationship(back_populates="webinar")
    chat_message: List["ChatMessage"] = Relationship(back_populates="webinar")
    
    @property
    def total_registrations(self) -> int:
        """Get total number of registrations"""
        return len(self.registrations)
    
    @property
    def total_attendees(self) -> int:
        """Get total number of attendees"""
        return sum(1 for reg in self.registrations if reg.attended)
    
    @property
    def attendance_rate(self) -> float:
        """Calculate attendance rate"""
        if not self.registrations:
            return 0.0
        return (self.total_attendees / self.total_registrations) * 100
    
    @property
    def is_upcoming(self) -> bool:
        """Check if webinar is upcoming"""
        return self.scheduled_at > datetime.utcnow() and self.status == WebinarStatus.SCHEDULED


class WebinarRegistration(SQLModel, table=True):
    """Webinar registration model""" 
    __tablename__ = "webinar_registration"

    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )    
    # Foreign keys
    webinar_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="webinar.id",default=None)
    user_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="users.id",default=None)
    
    # Registration details
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    attended: bool = Field(default=False)
    attendance_duration: int = Field(default=0)  # in seconds
    
    # Feedback
    feedback_rating: Optional[int] = Field(default=None, ge=1, le=5)
    feedback_comment: Optional[str] = Field(default=None, sa_type=Text) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    webinar: Webinar = Relationship(back_populates="webinar_registration")
    users: "User" = Relationship(back_populates="webinar_registration")
    
    @property
    def attendance_percentage(self) -> float:
        """Calculate attendance percentage"""
        if not self.webinar.duration or self.attendance_duration == 0:
            return 0.0
        webinar_duration_seconds = self.webinar.duration * 60
        return min((self.attendance_duration / webinar_duration_seconds) * 100, 100.0)


class ChatMessage(SQLModel, table=True):
    """Chat message model for webinars""" 
    __tablename__ = "chat_message" 

    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )     
    # Foreign keys
    webinar_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="webinar.id",default=None)
    user_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="users.id",default=None)
    
    # Message details
    message: str = Field(nullable=False, sa_type=Text)
    message_type: MessageType = Field(default=MessageType.TEXT)
    
    # Q&A functionality
    is_answered: bool = Field(default=False)
    answered_by: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    answer_text: Optional[str] = Field(default=None, sa_type=Text) 

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    webinar: Webinar = Relationship(back_populates="chat_message")
    users: "User" = Relationship(back_populates="chat_message", sa_relationship_kwargs={"foreign_keys": "[ChatMessage.user_id]"})
    answerer: Optional["User"] = Relationship(back_populates="chat_message",sa_relationship_kwargs={"foreign_keys": "[ChatMessage.answered_by]"})


# Import other models to avoid circular imports
from app.models.models.user import User

