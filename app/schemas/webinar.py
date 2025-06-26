
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime

from app.schemas.base import BaseSchema, TimestampMixin, PaginatedResponse, SearchParams
from app.models.models.webinar import WebinarStatus, MessageType


class WebinarCreateSchema(BaseSchema):
    """Webinar creation schema"""
    title: str = Field(..., min_length=1, max_length=200, description="Webinar title")
    description: Optional[str] = Field(None, description="Webinar description")
    scheduled_at: datetime = Field(..., description="Scheduled date and time")
    duration: int = Field(default=60, gt=0, description="Duration in minutes")
    join_url: str = Field(..., max_length=500, description="Join URL for the webinar")
    status: WebinarStatus = Field(default=WebinarStatus.SCHEDULED, description="Status of the webinar")
    organizer_id: str = Field(..., description="ID of the user organizing the webinar")

    @validator("scheduled_at")
    def validate_scheduled_at(cls, v):
        """Validate that scheduled time is in the future"""
        if v <= datetime.utcnow():
            raise ValueError("Scheduled time must be in the future")
        return v


class WebinarUpdateSchema(BaseSchema):
    """Webinar update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None)
    scheduled_at: Optional[datetime] = Field(None)
    duration: Optional[int] = Field(None, gt=0)
    join_url: Optional[str] = Field(None, max_length=500)
    status: Optional[WebinarStatus] = Field(None)
    organizer_id: Optional[str] = Field(None)


class WebinarListParams(SearchParams):
    """Webinar list query parameters"""
    status: Optional[WebinarStatus] = Field(None, description="Filter by status")
    organizer_id: Optional[str] = Field(None, description="Filter by organizer")
    upcoming: Optional[bool] = Field(None, description="Filter upcoming webinars")
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")


class WebinarSchema(BaseSchema, TimestampMixin):
    """Webinar response schema"""
    id: str
    title: str
    description: Optional[str]
    scheduled_at: datetime
    duration: int
    join_url: str
    status: WebinarStatus
    organizer_id: str
    
    # Statistics
    total_registrations: int = 0
    
    @property
    def is_upcoming(self) -> bool:
        """Check if webinar is upcoming"""
        return self.scheduled_at > datetime.utcnow() and self.status == WebinarStatus.SCHEDULED


class WebinarRegistrationSchema(BaseSchema, TimestampMixin):
    """Webinar registration response schema"""
    id: str
    webinar_id: str
    user_id: str
    registered_at: datetime
    
    # Related data
    webinar_title: Optional[str]
    user_name: Optional[str]


class ChatMessageCreateSchema(BaseSchema):
    """Chat message creation schema"""
    message: str = Field(..., min_length=1, max_length=1000, description="Message text")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Message type")


class ChatMessageSchema(BaseSchema, TimestampMixin):
    """Chat message response schema"""
    id: str
    webinar_id: str
    user_id: str
    user_name: str
    message: str
    message_type: MessageType
    is_answered: bool
    answered_by: Optional[str]
    answerer_name: Optional[str]
    answer_text: Optional[str]


class ChatMessageAnswerSchema(BaseSchema):
    """Chat message answer schema"""
    answer_text: str = Field(..., min_length=1, max_length=1000, description="Answer text")


class WebinarStatsSchema(BaseSchema):
    """Webinar statistics schema"""
    total_webinars: int
    upcoming_webinars: int
    completed_webinars: int
    total_registrations: int
    average_attendance_rate: float
    most_popular_webinars: List[dict]
    attendance_trends: List[dict]


class WebinarCalendarSchema(BaseSchema):
    """Webinar calendar schema"""
    date: str  # YYYY-MM-DD format
    webinars: List[WebinarSchema]


# Paginated response types
PaginatedWebinarsResponse = PaginatedResponse[WebinarSchema]
PaginatedWebinarRegistrationsResponse = PaginatedResponse[WebinarRegistrationSchema]
PaginatedChatMessagesResponse = PaginatedResponse[ChatMessageSchema]


