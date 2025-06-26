
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.models.review import ContentReview, ContentVersion, ReviewStatus, ContentTypeEnum
from app.schemas.review import (
    ContentReviewCreateSchema, ContentReviewSchema, ContentReviewUpdateSchema,
    ContentVersionCreateSchema, ContentVersionSchema, ReviewStatsSchema,
    BulkReviewActionSchema, ReviewAssignmentSchema, ContentReviewListParams
)
from app.core.security import get_current_user
from app.models.models.user import User

reviews_router = APIRouter()

# Content Review Routes

@reviews_router.post(
    "/", 
    response_model=ContentReviewSchema, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new content review"
)
async def create_content_review(
    review: ContentReviewCreateSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new content review request"""
    db_review = ContentReview.model_validate(review)
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    return db_review

@reviews_router.get(
    "/", 
    response_model=List[ContentReviewSchema],
    summary="Get all content reviews with optional filtering"
)
async def get_content_reviews(
    content_type: Optional[ContentTypeEnum] = Query(None, description="Filter by content type"),
    status_filter: Optional[ReviewStatus] = Query(None, alias="status", description="Filter by review status"),
    reviewer_id: Optional[UUID] = Query(None, description="Filter by reviewer ID"),
    submitter_id: Optional[UUID] = Query(None, description="Filter by submitter ID"),
    pending_only: Optional[bool] = Query(None, description="Show only pending reviews"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get content reviews with optional filtering"""
    query = select(ContentReview)
    
    # Apply filters
    if content_type:
        query = query.where(ContentReview.content_type == content_type)
    if status_filter:
        query = query.where(ContentReview.status == status_filter)
    if reviewer_id:
        query = query.where(ContentReview.reviewer_id == reviewer_id)
    if submitter_id:
        query = query.where(ContentReview.submitter_id == submitter_id)
    if pending_only:
        query = query.where(ContentReview.status == ReviewStatus.PENDING)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    reviews = session.exec(query).all()
    return reviews

@reviews_router.get(
    "/my-submissions", 
    response_model=List[ContentReviewSchema],
    summary="Get reviews for content submitted by current user"
)
async def get_my_submitted_reviews(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all reviews for content submitted by the current user"""
    reviews = session.exec(
        select(ContentReview).where(ContentReview.submitter_id == current_user.id)
    ).all()
    return reviews

@reviews_router.get(
    "/my-reviews", 
    response_model=List[ContentReviewSchema],
    summary="Get reviews assigned to current user"
)
async def get_my_assigned_reviews(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all reviews assigned to the current user"""
    reviews = session.exec(
        select(ContentReview).where(ContentReview.reviewer_id == current_user.id)
    ).all()
    return reviews

@reviews_router.get(
    "/{review_id}", 
    response_model=ContentReviewSchema,
    summary="Get a specific content review by ID"
)
async def get_content_review_by_id(
    review_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific content review by ID"""
    review = session.get(ContentReview, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return review

@reviews_router.put(
    "/{review_id}", 
    response_model=ContentReviewSchema,
    summary="Update a content review"
)
async def update_content_review(
    review_id: UUID,
    review_update: ContentReviewUpdateSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update a content review (typically by the assigned reviewer)"""
    review = session.get(ContentReview, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    # Check if current user is the assigned reviewer or has admin privileges
    if review.reviewer_id != current_user.id:
        # Add admin check here if needed
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this review")
    
    # Update the review
    review.sqlmodel_update(review_update.model_dump(exclude_unset=True))
    
    # Set reviewed_at timestamp if status is being changed to approved/rejected
    if review_update.status and review_update.status != ReviewStatus.PENDING:
        review.reviewed_at = datetime.utcnow()
    
    session.add(review)
    session.commit()
    session.refresh(review)
    return review

@reviews_router.put(
    "/{review_id}/assign", 
    response_model=ContentReviewSchema,
    summary="Assign a review to a reviewer"
)
async def assign_review(
    review_id: UUID,
    assignment: ReviewAssignmentSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Assign a review to a specific reviewer"""
    review = session.get(ContentReview, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    # Add admin/manager authorization check here if needed
    
    review.reviewer_id = UUID(assignment.reviewer_id)
    session.add(review)
    session.commit()
    session.refresh(review)
    return review

@reviews_router.delete(
    "/{review_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a content review"
)
async def delete_content_review(
    review_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a content review"""
    review = session.get(ContentReview, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    # Check authorization (submitter or admin)
    if review.submitter_id != current_user.id:
        # Add admin check here if needed
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this review")
    
    session.delete(review)
    session.commit()
    return

# Content Version Routes

@reviews_router.post(
    "/versions", 
    response_model=ContentVersionSchema, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new content version"
)
async def create_content_version(
    version: ContentVersionCreateSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new content version"""
    db_version = ContentVersion.model_validate(version)
    session.add(db_version)
    session.commit()
    session.refresh(db_version)
    return db_version

@reviews_router.get(
    "/versions/{content_id}", 
    response_model=List[ContentVersionSchema],
    summary="Get all versions for a specific content"
)
async def get_content_versions(
    content_id: str,
    content_type: ContentTypeEnum = Query(..., description="Content type"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all versions for a specific content"""
    versions = session.exec(
        select(ContentVersion)
        .where(ContentVersion.content_id == content_id)
        .where(ContentVersion.content_type == content_type)
        .order_by(ContentVersion.version_number.desc())
    ).all()
    return versions

# Statistics and Bulk Operations

@reviews_router.get(
    "/stats/overview", 
    response_model=ReviewStatsSchema,
    summary="Get review statistics overview"
)
async def get_review_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get review statistics overview"""
    # Get basic counts
    total_reviews = session.exec(select(ContentReview)).count()
    pending_reviews = session.exec(select(ContentReview).where(ContentReview.status == ReviewStatus.PENDING)).count()
    approved_reviews = session.exec(select(ContentReview).where(ContentReview.status == ReviewStatus.APPROVED)).count()
    rejected_reviews = session.exec(select(ContentReview).where(ContentReview.status == ReviewStatus.REJECTED)).count()
    
    # Get recent reviews
    recent_reviews = session.exec(
        select(ContentReview)
        .order_by(ContentReview.created_at.desc())
        .limit(10)
    ).all()
    
    # Get reviews by type and status (simplified)
    reviews_by_type = [
        {"type": "course", "count": session.exec(select(ContentReview).where(ContentReview.content_type == ContentTypeEnum.COURSE)).count()},
        {"type": "module", "count": session.exec(select(ContentReview).where(ContentReview.content_type == ContentTypeEnum.MODULE)).count()},
        {"type": "quiz", "count": session.exec(select(ContentReview).where(ContentReview.content_type == ContentTypeEnum.QUIZ)).count()},
    ]
    
    reviews_by_status = [
        {"status": "pending", "count": pending_reviews},
        {"status": "approved", "count": approved_reviews},
        {"status": "rejected", "count": rejected_reviews},
    ]
    
    return ReviewStatsSchema(
        total_reviews=total_reviews,
        pending_reviews=pending_reviews,
        approved_reviews=approved_reviews,
        rejected_reviews=rejected_reviews,
        reviews_by_type=reviews_by_type,
        reviews_by_status=reviews_by_status,
        recent_reviews=recent_reviews
    )

@reviews_router.post(
    "/bulk-action", 
    response_model=List[ContentReviewSchema],
    summary="Perform bulk actions on reviews"
)
async def bulk_review_action(
    bulk_action: BulkReviewActionSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Perform bulk actions on multiple reviews"""
    # Get all reviews by IDs
    reviews = session.exec(
        select(ContentReview).where(ContentReview.id.in_([UUID(rid) for rid in bulk_action.review_ids]))
    ).all()
    
    if not reviews:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No reviews found")
    
    # Update all reviews
    updated_reviews = []
    for review in reviews:
        # Check authorization for each review
        if review.reviewer_id != current_user.id:
            continue  # Skip reviews not assigned to current user
        
        review.status = bulk_action.action
        if bulk_action.review_notes:
            review.review_notes = bulk_action.review_notes
        if bulk_action.action != ReviewStatus.PENDING:
            review.reviewed_at = datetime.utcnow()
        
        session.add(review)
        updated_reviews.append(review)
    
    session.commit()
    
    # Refresh all updated reviews
    for review in updated_reviews:
        session.refresh(review)
    
    return updated_reviews

__all__ = ["reviews_router"]

