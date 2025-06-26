
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
    return analytics_service.record_learning_event(event_data, current_user.username)


@router.get("/dashboard-metrics", response_model=DashboardMetricsSchema)
async def get_dashboard_metrics(
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get key metrics for the learning dashboard"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_dashboard_metrics()


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
    return analytics_service.get_user_analytics(user_id, start_date, end_date)


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
    return analytics_service.get_course_analytics(course_id, start_date, end_date)


@router.get("/system", response_model=SystemAnalyticsSchema)
async def get_system_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get system-wide analytics"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_system_analytics(start_date, end_date)


@router.post("/reports/generate", response_model=ReportSchema, status_code=status.HTTP_202_ACCEPTED)
async def generate_report(
    report_request: ReportGenerationSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Generate a new report"""
    analytics_service = AnalyticsService(db)
    return analytics_service.generate_report(report_request, current_user.username)


@router.get("/reports/{report_id}", response_model=ReportSchema)
async def get_report_status(
    report_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get the status of a generated report"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_report_status(report_id)


@router.post("/export", response_model=ExportSchema, status_code=status.HTTP_202_ACCEPTED)
async def export_data(
    export_request: ExportRequestSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Export data from the system"""
    analytics_service = AnalyticsService(db)
    return analytics_service.export_data(export_request, current_user.username)


@router.get("/export/{export_id}", response_model=ExportSchema)
async def get_export_status(
    export_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get the status of a data export job"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_export_status(export_id)


# Create router instance for export
analytics_router = router


