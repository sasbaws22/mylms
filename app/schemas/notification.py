"""
Notification schemas
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.base import BaseSchema, TimestampMixin, PaginatedResponse, SearchParams
from app.models.models.notification import NotificationType, NotificationPriority


class NotificationCreate(BaseSchema):
    """Notification creation schema"""
    user_id: str = Field(..., description="User ID to send notification to")
    title: str = Field(..., min_length=1, max_length=200, description="Notification title")
    message: str = Field(..., min_length=1, description="Notification message")
    notification_type: NotificationType = Field(..., description="Notification type")
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM, description="Notification priority")
    action_url: Optional[str] = Field(None, max_length=500, description="Action URL")
    scheduled_for: Optional[datetime] = Field(None, description="Schedule notification for later")


class BulkNotificationCreateSchema(BaseSchema):
    """Bulk notification creation schema"""
    user_ids: List[str] = Field(..., min_items=1, description="List of user IDs")
    title: str = Field(..., min_length=1, max_length=200, description="Notification title")
    message: str = Field(..., min_length=1, description="Notification message")
    notification_type: NotificationType = Field(..., description="Notification type")
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM, description="Notification priority")
    action_url: Optional[str] = Field(None, max_length=500, description="Action URL")
    scheduled_for: Optional[datetime] = Field(None, description="Schedule notification for later")


class NotificationListParams(SearchParams):
    """Notification list query parameters"""
    notification_type: Optional[NotificationType] = Field(None, description="Filter by type")
    priority: Optional[NotificationPriority] = Field(None, description="Filter by priority")
    is_read: Optional[bool] = Field(None, description="Filter by read status")
    unread_only: Optional[bool] = Field(None, description="Show only unread notifications")


class NotificationSchema(BaseSchema, TimestampMixin):
    """Notification response schema"""
    id: str
    user_id: str
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority
    is_read: bool
    action_url: Optional[str]
    scheduled_for: Optional[datetime]
    sent_at: Optional[datetime]
    
    @property
    def is_sent(self) -> bool:
        """Check if notification has been sent"""
        return self.sent_at is not None
    
    @property
    def is_scheduled(self) -> bool:
        """Check if notification is scheduled for future"""
        return self.scheduled_for is not None and self.scheduled_for > datetime.utcnow()


class NotificationPreferencesSchema(BaseSchema, TimestampMixin):
    """Notification preferences response schema"""
    id: str
    user_id: str
    email_enabled: bool
    sms_enabled: bool
    push_enabled: bool
    assignment_notifications: bool
    reminder_notifications: bool
    achievement_notifications: bool
    webinar_notifications: bool


class NotificationPreferencesUpdateSchema(BaseSchema):
    """Notification preferences update schema"""
    email_enabled: Optional[bool] = Field(None, description="Enable email notifications")
    sms_enabled: Optional[bool] = Field(None, description="Enable SMS notifications")
    push_enabled: Optional[bool] = Field(None, description="Enable push notifications")
    assignment_notifications: Optional[bool] = Field(None, description="Enable assignment notifications")
    reminder_notifications: Optional[bool] = Field(None, description="Enable reminder notifications")
    achievement_notifications: Optional[bool] = Field(None, description="Enable achievement notifications")
    webinar_notifications: Optional[bool] = Field(None, description="Enable webinar notifications")


class NotificationStatsSchema(BaseSchema):
    """Notification statistics schema"""
    total_notifications: int
    unread_notifications: int
    notifications_by_type: List[dict]
    notifications_by_priority: List[dict]
    recent_notifications: List[NotificationSchema]


class NotificationMarkReadSchema(BaseSchema):
    """Schema for marking notifications as read"""
    notification_ids: List[str] = Field(..., min_items=1, description="List of notification IDs to mark as read")


class NotificationTemplateSchema(BaseSchema):
    """Notification template schema"""
    template_name: str
    title_template: str
    message_template: str
    notification_type: NotificationType
    priority: NotificationPriority
    variables: List[str] = []  # List of template variables


# Paginated response types
PaginatedNotificationsResponse = PaginatedResponse[NotificationSchema]

