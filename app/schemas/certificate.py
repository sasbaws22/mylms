
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.base import BaseSchema, TimestampMixin, PaginatedResponse
from app.models.models.certificate import CertificateType


class CertificateCreateSchema(BaseSchema):
    """Certificate creation schema"""
    user_id: str = Field(..., description="User ID")
    course_id: Optional[str] = Field(None, description="Course ID (if applicable)")
    certificate_type: CertificateType = Field(..., description="Type of certificate")
    issued_at: Optional[datetime] = Field(None, description="Date of issue (defaults to now)")
    expires_at: Optional[datetime] = Field(None, description="Expiration date (if applicable)")
    certificate_url: Optional[str] = Field(None, max_length=500, description="URL to the certificate file")


class CertificateUpdateSchema(BaseSchema):
    """Certificate update schema"""
    certificate_type: Optional[CertificateType] = Field(None, description="Type of certificate")
    issued_at: Optional[datetime] = Field(None, description="Date of issue")
    expires_at: Optional[datetime] = Field(None, description="Expiration date")
    certificate_url: Optional[str] = Field(None, max_length=500, description="URL to the certificate file")
    is_valid: Optional[bool] = Field(None, description="Is certificate valid")


class CertificateSchema(BaseSchema, TimestampMixin):
    """Certificate response schema"""
    id: str
    user_id: str
    course_id: Optional[str]
    certificate_type: CertificateType
    issued_at: datetime
    expires_at: Optional[datetime]
    certificate_url: Optional[str]
    verification_code: str
    is_valid: bool
    
    # Related data
    user_name: Optional[str]
    course_title: Optional[str]


# Paginated response types
PaginatedCertificatesResponse = PaginatedResponse[CertificateSchema]


