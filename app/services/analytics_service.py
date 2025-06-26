"""
Analytics service for tracking and reporting learning data
"""
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from fastapi import HTTPException, status
from datetime import datetime, date, timedelta
import uuid
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.models.analytics import LearningAnalytics, ActionType
from app.models.models.user import User
from app.models.models.course import Course, Enrollment
from app.models.models.module import Module
from app.models.models.quiz import QuizAttempt
from app.schemas.analytics import (
    LearningAnalyticsCreateSchema, LearningAnalyticsSchema,
    UserAnalyticsSchema, CourseAnalyticsSchema, SystemAnalyticsSchema,
    DashboardMetricsSchema, ReportGenerationSchema, ReportSchema, ExportRequestSchema, ExportSchema
)
from app.schemas.base import PaginatedResponse


class AnalyticsService:
    """Analytics and reporting service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def record_learning_event(self, event_data: LearningAnalyticsCreateSchema, user_id: str) -> Any :
        """Record a new learning event"""
        new_event = LearningAnalytics(
            user_id=user_id,
            course_id=event_data.course_id,
            module_id=event_data.module_id,
            action_type=event_data.action_type,
            action_data=event_data.action_data,
            timestamp=datetime.utcnow()
        )
        self.db.add(new_event)
        await self.db.commit()
        await self.db.refresh(new_event)
        return new_event

    async def get_dashboard_metrics(self) -> DashboardMetricsSchema:
        """Get key metrics for the learning dashboard"""
        total_user = await self.db.exec(select(func.count(User.id)))
        total_users = total_user.first()
        total_course = await self.db.exec(select(func.count(Course.id)))
        total_courses = total_course.first()


        total_enrollment = await self.db.exec(select(func.count(Enrollment.id)))
        total_enrollments = total_enrollment.first()
        
        completed_enrollment = await self.db.exec(select(func.count(Enrollment.id)).where(Enrollment.status == "completed"))
        completed_enrollments = completed_enrollment.first()
        completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0.0

        # Placeholder for more complex trend and top performers logic
        return DashboardMetricsSchema(
            total_users=total_users,
            total_courses=total_courses,
            total_enrollments=total_enrollments,
            completion_rate=completion_rate,

        )

    async def get_user_analytics(self, user_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> UserAnalyticsSchema:
        """Get detailed analytics for a specific user"""
        result = await self.db.exec(select(User).where(User.id == user_id))
        user = result.first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Placeholder for actual calculations
        return UserAnalyticsSchema(
            user_id=user.id,
            user_name=user.username,
            total_enrollments=len(user.enrollment),
            completed_courses=len(user.courses),
            quiz_attempts=len(user.quiz_attempts),
            webinar_attendance=len(user.webinars),
            total_points=len(user.user_points),
            total_certificates=len(user.certificates),
            total_badges=len(user.user_badges)
        )

    async def get_course_analytics(self, course_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> CourseAnalyticsSchema:
        """Get detailed analytics for a specific course"""
        courses = await self.db.exec(select(Course).where(Course.id == course_id))
        course = courses.first()
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

        # Placeholder for actual calculations
        return CourseAnalyticsSchema(
            course_id=course.id,
            course_title=course.title,
            category="N/A",
            total_enrollments= len(course.enrollment),
        )

    