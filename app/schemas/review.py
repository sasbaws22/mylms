"""
Review schemas
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.base import BaseSchema, TimestampMixin, PaginatedResponse, SearchParams
from app.models.models.review import ReviewStatus, ContentTypeEnum


class ContentReviewCreateSchema(BaseSchema):
    """Content review creation schema"""
    content_id: str = Field(..., description="ID of the content being reviewed")
    content_type: ContentTypeEnum = Field(..., description="Type of content being reviewed")
    submitter_id: str = Field(..., description="ID of the user submitting for review")
    review_notes: Optional[str] = Field(None, description="Initial review notes or comments")


class ContentReviewUpdateSchema(BaseSchema):
    """Content review update schema"""
    status: Optional[ReviewStatus] = Field(None, description="Review status")
    review_notes: Optional[str] = Field(None, description="Review notes or feedback")
    reviewed_at: Optional[datetime] = Field(None, description="When the review was completed")


class ContentReviewListParams(SearchParams):
    """Content review list query parameters"""
    content_type: Optional[ContentTypeEnum] = Field(None, description="Filter by content type")
    status: Optional[ReviewStatus] = Field(None, description="Filter by review status")
    reviewer_id: Optional[str] = Field(None, description="Filter by reviewer ID")
    submitter_id: Optional[str] = Field(None, description="Filter by submitter ID")
    pending_only: Optional[bool] = Field(None, description="Show only pending reviews")


class ContentReviewSchema(BaseSchema, TimestampMixin):
    """Content review response schema"""
    id: str
    content_id: str
    content_type: ContentTypeEnum
    reviewer_id: Optional[str]
    submitter_id: str
    status: ReviewStatus
    review_notes: Optional[str]
    reviewed_at: Optional[datetime]
    
    @property
    def is_pending(self) -> bool:
        """Check if review is pending"""
        return self.status == ReviewStatus.PENDING
    
    @property
    def is_approved(self) -> bool:
        """Check if review is approved"""
        return self.status == ReviewStatus.APPROVED


class ContentVersionCreateSchema(BaseSchema):
    """Content version creation schema"""
    content_id: str = Field(..., description="ID of the content")
    content_type: ContentTypeEnum = Field(..., description="Type of content")
    version_number: int = Field(..., description="Version number")
    changes_summary: Optional[str] = Field(None, description="Summary of changes made")
    created_by: str = Field(..., description="ID of the user creating the version")
    is_current: bool = Field(default=False, description="Whether this is the current version")


class ContentVersionSchema(BaseSchema, TimestampMixin):
    """Content version response schema"""
    id: str
    content_id: str
    content_type: ContentTypeEnum
    version_number: int
    changes_summary: Optional[str]
    created_by: str
    is_current: bool


class ReviewStatsSchema(BaseSchema):
    """Review statistics schema"""
    total_reviews: int
    pending_reviews: int
    approved_reviews: int
    rejected_reviews: int
    reviews_by_type: List[dict]
    reviews_by_status: List[dict]
    recent_reviews: List[ContentReviewSchema]


class BulkReviewActionSchema(BaseSchema):
    """Schema for bulk review actions"""
    review_ids: List[str] = Field(..., min_items=1, description="List of review IDs")
    action: ReviewStatus = Field(..., description="Action to perform on reviews")
    review_notes: Optional[str] = Field(None, description="Notes for the bulk action")


class ReviewAssignmentSchema(BaseSchema):
    """Schema for assigning reviews to reviewers"""
    review_id: str = Field(..., description="Review ID to assign")
    reviewer_id: str = Field(..., description="ID of the reviewer to assign")


# Paginated response types
PaginatedContentReviewsResponse = PaginatedResponse[ContentReviewSchema]
PaginatedContentVersionsResponse = PaginatedResponse[ContentVersionSchema]

# Aliases for backward compatibility
ReviewCreate = ContentReviewCreateSchema
ReviewRead = ContentReviewSchema
ReviewUpdate = ContentReviewUpdateSchema
ReviewListParams = ContentReviewListParams

