"""
User management schemas
"""
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime 
import uuid

from app.schemas.base import BaseSchema, TimestampMixin, PaginatedResponse, SearchParams


class UserListParams(SearchParams):
    """User list query parameters"""
    is_active: Optional[bool] = Field(None, description="Filter by active status")


class UserSummarySchema(BaseSchema):
    """User summary schema for lists"""
    id: uuid.UUID
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    last_login: Optional[datetime]
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"


class UserDetailSchema(BaseSchema, TimestampMixin):
    """Detailed user schema"""
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    phone_number: Optional[str]
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    avatar_url: Optional[str]
    
    # Statistics
    total_enrollments: int = 0
    completed_courses: int = 0
    total_points: int = 0
    total_certificates: int = 0
    total_badges: int = 0
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"


class UserStatsSchema(BaseSchema):
    """User statistics schema"""
    total_users: int
    active_users: int
    new_users_this_month: int 

    class Config:
        orm_mode = True


# Paginated response types
PaginatedUsersResponse = PaginatedResponse[UserSummarySchema]


# Import schemas from auth module
from app.schemas.auth import (
    UserResponseSchema, 
    UserProfileSchema, 
    UserUpdateSchema, 
    UserCreateSchema
)


