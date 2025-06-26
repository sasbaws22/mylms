"""
Certificate and gamification database models
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON, Text
import enum 
import uuid 
import sqlalchemy.dialects.postgresql as pg



class CertificateType(str, enum.Enum):
    """Certificate type enumeration"""
    COMPLETION = "completion"
    ACHIEVEMENT = "achievement"
    PARTICIPATION = "participation"


class BadgeType(str, enum.Enum):
    """Badge type enumeration"""
    COURSE_COMPLETION = "course_completion"
    STREAK = "streak"
    PARTICIPATION = "participation"
    ACHIEVEMENT = "achievement"


class PointsSource(str, enum.Enum):
    """Points source enumeration"""
    COURSE_COMPLETION = "course_completion"
    QUIZ_SCORE = "quiz_score"
    PARTICIPATION = "participation"
    BONUS = "bonus"


class Certificate(SQLModel, table=True): 
    __tablename__ = "certificate"
    """Certificate model"""
    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )    
    # Foreign keys
    user_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="users.id",default=None)
    course_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="course.id",default=None)
    
    # Certificate details
    certificate_type: CertificateType = Field(default=CertificateType.COMPLETION)
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)
    
    # Certificate file and verification
    certificate_url: Optional[str] = Field(default=None, max_length=500)
    verification_code: str = Field(unique=True, nullable=False, max_length=50)
    is_valid: bool = Field(default=True) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    users: "User" = Relationship(back_populates="certificates")
    course: "Course" = Relationship(back_populates="certificates")
    
    @property
    def is_expired(self) -> bool:
        """Check if certificate is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at


class Badge(SQLModel, table=True): 
    __tablename__ = "badge"
    """Badge model"""
    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )    
    # Badge details
    name: str = Field(unique=True, nullable=False, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    icon_url: Optional[str] = Field(default=None, max_length=500)
    
    # Badge criteria and value
    criteria: dict = Field(default_factory=dict, sa_type=JSON)
    points_value: int = Field(default=0)
    badge_type: BadgeType = Field(default=BadgeType.ACHIEVEMENT) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    user_badges: List["UserBadge"] = Relationship(back_populates="badge")
    
    @property
    def total_earned(self) -> int:
        """Get total number of times this badge was earned"""
        return len(self.user_badges)


class UserBadge(SQLModel, table=True):
    """User badge model - tracks badges earned by users""" 
    __tablename__ = "user_badges"
    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )       
    # Foreign keys
    user_id:Optional[uuid.UUID] =  Field( nullable=True, foreign_key="users.id",default=None)
    badge_id:Optional[uuid.UUID] =  Field( nullable=True, foreign_key="badge.id",default=None)
    
    # Badge earning details
    earned_at: datetime = Field(default_factory=datetime.now)
    reason: Optional[str] = Field(default=None, max_length=255) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    users: "User" = Relationship(back_populates="user_badges", sa_relationship_kwargs={"foreign_keys": "[UserBadge.user_id]"})
    badge: Badge = Relationship(back_populates="user_badges")


class UserPoints(SQLModel, table=True):
    """User points model - tracks points earned by users""" 
    __tablename__ = "user_points"
    
    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    ) 
    # Foreign key
    user_id:Optional[uuid.UUID] =  Field( nullable=True, foreign_key="users.id",default=None)
    
    # Points details
    points: int = Field(default=0)
    points_source: PointsSource = Field(nullable=False)
    source_id: Optional[str] = Field(default=None)  # ID of related entity (course, quiz, etc.)
    earned_at: datetime = Field(default_factory=datetime.now)
    description: Optional[str] = Field(default=None, max_length=255) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    users: "User" = Relationship(back_populates="user_points", sa_relationship_kwargs={"foreign_keys": "[UserPoints.user_id]"})


# Import other models to avoid circular imports
from app.models.models.user import User
from app.models.models.course import Course

