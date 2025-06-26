"""
Progress service for tracking user learning progress
"""
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from fastapi import HTTPException, status
from datetime import datetime

from app.models.models.progress import  ModuleProgress,  ProgressStatus,ContentProgress
from app.models.models.course import Course, Enrollment, EnrollmentStatus
from app.models.models.module import Module, Video, Document, ContentType 
from app.models.models.quiz import Quiz, QuizAttempt
from app.models.models.user import User
from app.schemas.progress import (
    UserCourseProgressSchema, ModuleProgressSchema, ContentProgressSchema,
    ProgressUpdateSchema
)
from app.schemas.base import PaginatedResponse


class ProgressService:
    """Progress tracking service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_user_course_progress(self, user_id: str, page: int = 1, limit: int = 20) -> PaginatedResponse[UserCourseProgressSchema]:
        """Get paginated list of course progress for a specific user"""
        # Verify user exists
        users = await self.db.exec(select(User).where(User.id == user_id))
        user = users.first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        query = select(Enrollment).where(Enrollment.user_id == user_id)
        
        tota = await self.db.exec(select(func.count(Enrollment.id)).where(Enrollment.user_id == user_id))
        total = tota.first()
        
        offset = (page - 1) * limit
        enrollment = await self.db.exec(query.offset(offset).limit(limit))
        enrollments = enrollment.all()
        
        course_progress_list = []
        for enrollment in enrollments:
            courses = await self.db.exec(select(Course).where(Course.id == enrollment.course_id))
            course = courses.first()
            if not course:
                continue
            
            # Calculate course progress
            total_modules = len(course.modules)
            completed_module = await self.db.exec(
                select(func.count(ModuleProgress.id)).where(
                    (ModuleProgress.enrollment_id == enrollment.id) &
                    (ModuleProgress.status == ProgressStatus.COMPLETED)
                )
            )
            completed_modules = completed_module.first()
            
            progress_percentage = (completed_modules / total_modules * 100) if total_modules > 0 else 0
            
            course_progress_list.append(UserCourseProgressSchema(
                enrollment_id=enrollment.id,
                user_id=user_id,
                course_id=course.id,
                course_title=course.title,
                enrollment_status=enrollment.status,
                progress_percentage=progress_percentage,
                started_at=enrollment.started_at,
                completed_at=enrollment.completed_at,
                due_date=enrollment.due_date,
                total_modules=total_modules,
                completed_modules=completed_modules,
                total_time_spent=0, # Placeholder
                last_accessed=enrollment.updated_at # Or a more accurate last accessed timestamp
            ))
        
        return PaginatedResponse.create(course_progress_list, total, page, limit)
    
    async def get_user_progress_for_course(self, user_id: str, course_id: str) -> UserCourseProgressSchema:
        """Get detailed progress for a user in a specific course"""
        enrollments = await self.db.exec(
            select(Enrollment).where(
                (Enrollment.user_id == user_id) & (Enrollment.course_id == course_id)
            )
        )
        enrollment = enrollments.first()
        
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not enrolled in this course"
            )
        
        courses = await self.db.exec(select(Course).where(Course.id == course_id))
        course = courses.first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        total_modules = len(course.modules)
        completed_moduless =await  self.db.exec(
            select(func.count(ModuleProgress.id)).where(
                (ModuleProgress.enrollment_id == enrollment.id) &
                (ModuleProgress.status == ProgressStatus.COMPLETED)
            )
        )
        completed_modules = completed_moduless.first()
        
        progress_percentage = (completed_modules / total_modules * 100) if total_modules > 0 else 0
        
        return UserCourseProgressSchema(
            enrollment_id=enrollment.id,
            user_id=user_id,
            course_id=course.id,
            course_title=course.title,
            enrollment_status=enrollment.status,
            progress_percentage=progress_percentage,
            started_at=enrollment.started_at,
            completed_at=enrollment.completed_at,
            due_date=enrollment.due_date,
            total_modules=total_modules,
            completed_modules=completed_modules,
            total_time_spent=0, # Placeholder
            last_accessed=enrollment.updated_at # Or a more accurate last accessed timestamp
        )
    
    async def update_content_progress(self, user_id: str, progress_data: ProgressUpdateSchema) -> ContentProgressSchema:
        """Update progress for a specific content item (module, video, document, quiz)"""
        # Find the enrollment for the user and course/module
        enrollments = await self.db.exec(
            select(Enrollment).where(
                (Enrollment.user_id == user_id) &
                (Enrollment.course_id == progress_data.course_id)
            )
        )
        enrollment = enrollments.first()

        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not enrolled in this course"
            )

        # Get or create ModuleProgress
        module_progresss = await self.db.exec(
            select(ModuleProgress).where(
                (ModuleProgress.enrollment_id == enrollment.id) &
                (ModuleProgress.module_id == progress_data.module_id)
            )
        ) 
        module_progress = module_progresss.first()

        if not module_progress:
            module_progress = ModuleProgress(
                enrollment_id=enrollment.id,
                module_id=progress_data.module_id,
                user_id=user_id,
                status=ProgressStatus.IN_PROGRESS,
                started_at=datetime.utcnow(),
                time_spent=0
            )
            self.db.add(module_progress)
            self.db.flush()

        # Update ContentProgress
        content_progresss = await  self.db.exec(
            select(ContentProgress).where(
                (ContentProgress.module_progress_id == module_progress.id) &
                (ContentProgress.content_type == progress_data.content_type)
            )
        )
        content_progress = content_progresss.first()

        if not content_progress:
            content_progress = ContentProgress(
                module_progress_id=module_progress.id,
                content_type=progress_data.content_type,
                status=progress_data.status,
                progress_percentage=progress_data.progress_percentage,
                time_spent=progress_data.time_spent or 0,
                last_accessed=datetime.now()
            )
        else:
            content_progress.status = progress_data.status
            content_progress.progress_percentage = progress_data.progress_percentage
            content_progress.time_spent += progress_data.time_spent or 0
            content_progress.last_accessed = datetime.utcnow()
        
        self.db.add(content_progress)
        await self.db.commit()
        await self.db.refresh(content_progress)

        # Update module progress based on content progress
        await self._update_module_progress_status(module_progress.id)
        await self._update_enrollment_progress_status(enrollment.id)

        return ContentProgressSchema.model_validate(content_progress)

    async def get_module_content_progress(self, user_id: str, module_id: str) -> List[ContentProgressSchema]:
        """Get progress for all content items within a module for the current user"""
        modules = await self.db.exec(select(Module).where(Module.id == module_id))
        module = modules.first()
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )

        enrollments =await  self.db.exec(
            select(Enrollment).where(
                (Enrollment.user_id == user_id) &
                (Enrollment.course_id == module.course_id)
            )
        )
        enrollment = enrollments.first()

        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not enrolled in this course"
            )

        module_progresss =await  self.db.exec(
            select(ModuleProgress).where(
                (ModuleProgress.enrollment_id == enrollment.id) &
                (ModuleProgress.module_id == module_id)
            )
        )
        module_progress = module_progresss.first()

        if not module_progress:
            return [] # No progress yet for this module

        content_progress_lists = await self.db.exec(
            select(ContentProgress).where(ContentProgress.module_progress_id == module_progress.id)
        )
        content_progress_list = content_progress_lists.all()

        return [ContentProgressSchema.model_validate(cp) for cp in content_progress_list]

    async def _update_module_progress_status(self, module_progress_id: str):
        module_progresss = await self.db.exec(select(ModuleProgress).where(ModuleProgress.id == module_progress_id))
        module_progress = module_progresss.first() 

        if not module_progress:
            return

        all_content_progresss = await self.db.exec(
            select(ContentProgress).where(ContentProgress.module_progress_id == module_progress_id)
        )
        all_content_progress = all_content_progresss.all()

        if not all_content_progress:
            module_progress.status = ProgressStatus.NOT_STARTED
        else:
            completed_count = sum(1 for cp in all_content_progress if cp.status == ProgressStatus.COMPLETED)
            if completed_count == len(all_content_progress):
                module_progress.status = ProgressStatus.COMPLETED
                module_progress.completed_at = datetime.utcnow()
            elif completed_count > 0:
                module_progress.status = ProgressStatus.IN_PROGRESS
            else:
                module_progress.status = ProgressStatus.NOT_STARTED
        
        self.db.add(module_progress)
        await self.db.commit()
        await self.db.refresh(module_progress)

    async def _update_enrollment_progress_status(self, enrollment_id: str):
        enrollments = await self.db.exec(select(Enrollment).where(Enrollment.id == enrollment_id))
        enrollment = enrollments.first()
        if not enrollment:
            return

        courses = await self.db.exec(select(Course).where(Course.id == enrollment.course_id))
        course = courses.first()
        if not course:
            return

        total_modules = len(course.modules)
        if total_modules == 0:
            enrollment.progress_percentage = 100.0
            enrollment.status = EnrollmentStatus.COMPLETED
        else:
            completed_modules_counts = await self.db.exec(
                select(func.count(ModuleProgress.id)).where(
                    (ModuleProgress.enrollment_id == enrollment_id) &
                    (ModuleProgress.status == ProgressStatus.COMPLETED)
                )
            )
            completed_modules_count = completed_modules_counts.first() or 0
            
            enrollment.progress_percentage = (completed_modules_count / total_modules * 100) if total_modules > 0 else 0
            
            if completed_modules_count == total_modules:
                enrollment.status = EnrollmentStatus.COMPLETED
                enrollment.completed_at = datetime.utcnow()
            elif completed_modules_count > 0:
                enrollment.status = EnrollmentStatus.IN_PROGRESS
            else:
                enrollment.status = EnrollmentStatus.ENROLLED # Or NOT_STARTED if that's a status
        
        self.db.add(enrollment)
        await self.db.commit()
        await self.db.refresh(enrollment)


