"""
Base schemas with common patterns for API requests and responses
"""
from datetime import datetime
from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

# Generic type for paginated responses
T = TypeVar('T')


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True
    )


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints"""
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    page: int
    limit: int
    pages: int
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int, limit: int):
        """Create paginated response"""
        pages = (total + limit - 1) // limit  # Ceiling division
        return cls(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages
        )


class MessageResponse(BaseSchema):
    """Standard message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseSchema):
    """Standard error response"""
    detail: str
    error_code: Optional[str] = None
    success: bool = False


class HealthCheckResponse(BaseSchema):
    """Health check response"""
    status: str
    app_name: str
    version: str
    timestamp: float


class SearchParams(BaseModel):
    """Search parameters"""
    search: Optional[str] = Field(default=None, description="Search query")
    sort_by: Optional[str] = Field(default="created_at", description="Sort field")
    sort_order: Optional[str] = Field(default="desc",description="Sort order")


# Common enums for API responses
class StatusEnum(str, Enum):
    """Generic status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

