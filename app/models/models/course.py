"""
Course-related database models
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON, Text
import enum 
import uuid 
import sqlalchemy.dialects.postgresql as pg




class CourseStatus(str, enum.Enum):
    """Course status enumeration"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class DifficultyLevel(str, enum.Enum):
    """Difficulty level enumeration"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class EnrollmentStatus(str, enum.Enum):
    """Enrollment status enumeration"""
    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DROPPED = "dropped"


class Category(SQLModel, table=True):
    """Category model for organizing courses""" 
    __tablename__ = "category" 
    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )    
        
    name: str = Field(unique=True, nullable=False, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    parent_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="category.id",default=None)
    color_code: Optional[str] = Field(default=None, max_length=7)  # Hex color code 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    courses: List["Course"] = Relationship(back_populates="category")
    parent: Optional["Category"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    children: List["Category"] = Relationship(back_populates="parent")


class Course(SQLModel, table=True):
    """Course model""" 
    __tablename__ = "course" 

    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )     
    title: str = Field(nullable=False, max_length=200)
    description: Optional[str] = Field(default=None, sa_type=Text)
    
    # Foreign keys
    category_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="category.id",default=None)
    creator_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="users.id",default=None)
    # Course properties
    status: CourseStatus = Field(default=CourseStatus.DRAFT)
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    estimated_duration: int = Field(default=0)  # in minutes
    is_mandatory: bool = Field(default=False)
    
    # Course metadata
    prerequisites: List[str] = Field(default_factory=list, sa_type=JSON)  # List of course IDs
    tags: List[str] = Field(default_factory=list, sa_type=JSON)
    thumbnail_url: Optional[str] = Field(default=None, max_length=500)
    
    # Publishing information
    published_at: Optional[datetime] = Field(default=None) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    category: Category = Relationship(back_populates="courses")
    users: "User" = Relationship(back_populates="courses")
    modules: List["Module"] = Relationship(back_populates="course")
    enrollment: List["Enrollment"] = Relationship(back_populates="course")
    certificates: List["Certificate"] = Relationship(back_populates="course")
    content_reviews: List["ContentReview"] = Relationship(back_populates="course") 
    learning_analytics: Optional["LearningAnalytics"] = Relationship(
        back_populates="course"
    )
    
    @property
    def total_modules(self) -> int:
        """Get total number of modules in the course"""
        return len(self.modules)
    
    @property
    def total_enrollments(self) -> int:
        """Get total number of enrollments"""
        return len(self.enrollment)
    
    @property
    def completion_rate(self) -> float:
        """Calculate course completion rate"""
        if not self.enrollments:
            return 0.0
        completed = sum(1 for enrollment in self.enrollments if enrollment.status == EnrollmentStatus.COMPLETED)
        return (completed / len(self.enrollments)) * 100


class Enrollment(SQLModel, table=True):
    """Enrollment model linking users to courses"""
    __tablename__  = "enrollment" 
    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    ) 
    # Foreign keys
    user_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="users.id",default=None)
    course_id:Optional[uuid.UUID] = Field( nullable=True, foreign_key="course.id",default=None)
    
    # Enrollment details
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    progress_percentage: float = Field(default=0.0)
    status: EnrollmentStatus = Field(default=EnrollmentStatus.ENROLLED)
    
    # Assignment details
    assigned_by: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    due_date: Optional[datetime] = Field(default=None) 
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now})
    
    # Relationships
    users: "User" = Relationship(back_populates="enrollment",sa_relationship_kwargs={"foreign_keys": "[Enrollment.user_id]"})
    course: Course = Relationship(back_populates="enrollment")
    assigned_by_user: Optional["User"] = Relationship(back_populates="enrollment",sa_relationship_kwargs={"foreign_keys": "[Enrollment.assigned_by]"})
    module_progress: List["ModuleProgress"] = Relationship(back_populates="enrollment")
    
    @property
    def is_overdue(self) -> bool:
        """Check if enrollment is overdue"""
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date and self.status != EnrollmentStatus.COMPLETED
# Import other models to avoid circular imports
from app.models.models.user import User
from app.models.models.module import Module
from app.models.models.progress import ModuleProgress
from app.models.models.certificate import Certificate
from app.models.models.review import ContentReview
from app.models.models.analytics import LearningAnalytics
