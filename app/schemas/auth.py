"""
Authentication and authorization schemas
"""
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime 
from uuid import UUID

from app.schemas.base import BaseSchema, TimestampMixin


class LoginSchema(BaseSchema):
    """Login request schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class TokenResponseSchema(BaseSchema):
    """Token response schema"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class RefreshTokenSchema(BaseSchema):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="Refresh token")


class UserRegistrationSchema(BaseSchema):
    """User registration request schema"""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password")
    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    
    @validator("password")
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class ForgotPasswordSchema(BaseSchema):
    """Forgot password request schema"""
    email: EmailStr = Field(..., description="User email address")


class ResetPasswordSchema(BaseSchema):
    """Reset password request schema"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator("new_password")
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class ChangePasswordSchema(BaseSchema):
    """Change password request schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator("new_password")
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserResponseSchema(BaseSchema, TimestampMixin):
    """User response schema"""
    id: UUID
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    avatar_url: Optional[str]
    
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"


class UserProfileSchema(BaseSchema, TimestampMixin):
    """User profile schema with additional details"""
    id: UUID
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    avatar_url: Optional[str]
    total_points: int = 0
    total_certificates: int = 0
    total_badges: int = 0
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"


class UserUpdateSchema(BaseSchema):
    """User update request schema"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserCreateSchema(BaseSchema):
    """User creation schema for admin use"""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    password: Optional[str] = Field(None, min_length=8, description="Password (auto-generated if not provided)")
    is_active: bool = Field(default=True, description="User active status")


class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None
    email: Optional[str] = None 

    class Config:
        orm_mode = True


