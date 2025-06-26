
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import Optional, List
from datetime import date

from app.db.database import get_session
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    LearningAnalyticsCreateSchema, LearningAnalyticsSchema,
    UserAnalyticsSchema, CourseAnalyticsSchema, SystemAnalyticsSchema,
    DepartmentAnalyticsSchema, LearningTrendSchema, EngagementMetricsSchema,
    ReportGenerationSchema, ReportSchema, DashboardMetricsSchema, ExportRequestSchema, ExportSchema,
    AnalyticsDateRangeParams
)
from app.schemas.base import MessageResponse
from app.core.security import access_token_bearer 
from app.schemas.auth import TokenData

router = APIRouter()


@router.post("/learning-events", response_model=LearningAnalyticsSchema, status_code=status.HTTP_201_CREATED)
async def create_learning_event(
    event_data: LearningAnalyticsCreateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Record a new learning event"""
    analytics_service = AnalyticsService(db)
    id = current_user.get("sub")
    return await analytics_service.record_learning_event(event_data, id)


@router.get("/dashboard-metrics", response_model=DashboardMetricsSchema)
async def get_dashboard_metrics(
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get key metrics for the learning dashboard"""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_dashboard_metrics()


@router.get("/users/{user_id}", response_model=UserAnalyticsSchema)
async def get_user_analytics(
    user_id: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get detailed analytics for a specific user"""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_user_analytics(user_id, start_date, end_date)


@router.get("/courses/{course_id}", response_model=CourseAnalyticsSchema)
async def get_course_analytics(
    course_id: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get detailed analytics for a specific course"""
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_course_analytics(course_id, start_date, end_date)



# Create router instance for export
analytics_router = router


