"""
Course service for course management operations
"""
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from fastapi import HTTPException, status,Depends,Request
from datetime import datetime

from app.models.models.course import Course, Category, Enrollment, CourseStatus, EnrollmentStatus
from app.models.models.user import User
from app.schemas.course import (
    CourseCreateSchema, CourseUpdateSchema, CourseDetailSchema,
    CourseSummarySchema, CourseListParams, CourseStatsSchema,
    CategoryCreateSchema, CategoryUpdateSchema, CategorySchema,
    EnrollmentCreateSchema, EnrollmentUpdateSchema, EnrollmentSchema,
    EnrollmentListParams, BulkEnrollmentSchema
)
from app.schemas.base import PaginatedResponse
from app.services.email_service import EmailService 
from app.core.security import access_token_bearer 
from app.schemas.auth import TokenData 
from app.utils.audit import audit_service


class CourseService:
    """Course management service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()
    
    async def get_courses(self, params: CourseListParams, page: int = 1, limit: int = 20) -> PaginatedResponse[CourseSummarySchema]:
        """Get paginated list of courses"""
        query = select(Course)
        
        # Apply filters
        if params.category_id:
            query = query.where(Course.category_id == params.category_id)
        
        if params.difficulty:
            query = query.where(Course.difficulty_level == params.difficulty)
        
        if params.status:
            query = query.where(Course.status == params.status)
        
        if params.creator_id:
            query = query.where(Course.creator_id == params.creator_id)
        
        if params.is_mandatory is not None:
            query = query.where(Course.is_mandatory == params.is_mandatory)
        
        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                (Course.title.ilike(search_term)) |
                (Course.description.ilike(search_term))
            )
        
        # Apply sorting
        if params.sort_by == "title":
            if params.sort_order == "desc":
                query = query.order_by(Course.title.desc())
            else:
                query = query.order_by(Course.title.asc())
        elif params.sort_by == "difficulty":
            if params.sort_order == "desc":
                query = query.order_by(Course.difficulty_level.desc())
            else:
                query = query.order_by(Course.difficulty_level.asc())
        else:  # Default to created_at
            if params.sort_order == "desc":
                query = query.order_by(Course.created_at.desc())
            else:
                query = query.order_by(Course.created_at.asc())
        
        # Get total count
        total_query = select(func.count(Course.id))
        if params.category_id:
            total_query = total_query.where(Course.category_id == params.category_id)
        if params.difficulty:
            total_query = total_query.where(Course.difficulty_level == params.difficulty)
        if params.status:
            total_query = total_query.where(Course.status == params.status)
        if params.creator_id:
            total_query = total_query.where(Course.creator_id == params.creator_id)
        if params.is_mandatory is not None:
            total_query = total_query.where(Course.is_mandatory == params.is_mandatory)
        if params.search:
            search_term = f"%{params.search}%"
            total_query = total_query.where(
                (Course.title.ilike(search_term)) |
                (Course.description.ilike(search_term))
            )
        
        tota = await self.db.exec(total_query)
        total = tota.first()
        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        course = await self.db.exec(query)
        courses = course.all()
        
        # Convert to summary schemas
        course_summaries = []
        for course in courses:
            categor =await  self.db.exec(select(Category).where(Category.id == course.category_id))
            category = categor.first()
            creato = await self.db.exec(select(User).where(User.id == course.creator_id))
            creator = creato.first()
            
            # Count modules and enrollments
            total_modules = len(course.modules)
            total_enrollments = len(course.enrollments)
            
            course_summaries.append(CourseSummarySchema(
                id=course.id,
                title=course.title,
                description=course.description,
                category_name=category.name if category else "Unknown",
                creator_name=creator.full_name if creator else "Unknown",
                status=course.status,
                difficulty_level=course.difficulty_level,
                estimated_duration=course.estimated_duration,
                is_mandatory=course.is_mandatory,
                thumbnail_url=course.thumbnail_url,
                total_modules=total_modules,
                total_enrollments=total_enrollments,
                created_at=course.created_at
            ))
        
        return PaginatedResponse.create(course_summaries, total, page, limit)
    
    def get_course_by_id(self, course_id: str, user_id: Optional[str] = None) -> CourseDetailSchema:
        """Get course by ID with detailed information"""
        course = self.db.exec(select(Course).where(Course.id == course_id)).first()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Get related data
        category = self.db.exec(select(Category).where(Category.id == course.category_id)).first()
        creator = self.db.exec(select(User).where(User.id == course.creator_id)).first()
        
        # Calculate statistics
        total_modules = len(course.modules)
        total_enrollments = len(course.enrollments)
        completed_enrollments = len([e for e in course.enrollments if e.status == EnrollmentStatus.COMPLETED])
        completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
        
        # Get user enrollment if user_id provided
        user_enrollment = None
        user_progress = 0.0
        if user_id:
            enrollment = self.db.exec(
                select(Enrollment).where(
                    (Enrollment.user_id == user_id) & (Enrollment.course_id == course_id)
                )
            ).first()
            if enrollment:
                user_enrollment = EnrollmentSchema.model_validate(enrollment)
                user_progress = enrollment.progress_percentage
        
        return CourseDetailSchema(
            id=course.id,
            title=course.title,
            description=course.description,
            category_id=course.category_id,
            category_name=category.name if category else "Unknown",
            creator_id=course.creator_id,
            creator_name=creator.full_name if creator else "Unknown",
            status=course.status,
            difficulty_level=course.difficulty_level,
            estimated_duration=course.estimated_duration,
            is_mandatory=course.is_mandatory,
            prerequisites=course.prerequisites,
            tags=course.tags,
            thumbnail_url=course.thumbnail_url,
            published_at=course.published_at,
            total_modules=total_modules,
            total_enrollments=total_enrollments,
            completion_rate=completion_rate,
            user_enrollment=user_enrollment,
            user_progress=user_progress,
            created_at=course.created_at,
            updated_at=course.updated_at
        )
    
    async def create_course(self, course_data: CourseCreateSchema, request:Request,creator_id: str,current_user:TokenData=Depends(access_token_bearer)) -> CourseDetailSchema:
        """Create a new course"""
        # Validate category
        categor = await self.db.exec(select(Category).where(Category.id == course_data.category_id))
        category = categor.first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid category ID"
            )
        
        # Validate prerequisites
        if course_data.prerequisites:
            for prereq_id in course_data.prerequisites:
                prereq_courses = await self.db.exec(select(Course).where(Course.id == prereq_id))
                prereq_course = prereq_courses.first()
                if not prereq_course:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid prerequisite course ID: {prereq_id}"
                    )
        
        # Create new course
        new_course = Course(
            title=course_data.title,
            description=course_data.description,
            category_id=course_data.category_id,
            creator_id=creator_id,
            difficulty_level=course_data.difficulty_level,
            estimated_duration=course_data.estimated_duration,
            is_mandatory=course_data.is_mandatory,
            prerequisites=course_data.prerequisites,
            tags=course_data.tags,
            thumbnail_url=course_data.thumbnail_url,
            status=CourseStatus.DRAFT
        )
        
        self.db.add(new_course)
        await self.db.commit()
        await self.db.refresh(new_course) 

        await  audit_service.log_create(
        db= self.db,
        user_id= current_user.get("sub"), 
        entity_type= new_course.__tablename__,
        entity_id=new_course.id,
        ip_address=request.client.host if request.client else None,
        details={"email": current_user.get("email")})
        
        return await self.get_course_by_id(new_course.id)
    
    async def update_course(self, course_id: str,request:Request, course_data: CourseUpdateSchema,current_user:TokenData=Depends(access_token_bearer)) -> CourseDetailSchema:
        """Update course information"""
        courses = await self.db.exec(select(Course).where(Course.id == course_id))
        course = courses.first()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Update fields
        if course_data.title is not None:
            course.title = course_data.title
        if course_data.description is not None:
            course.description = course_data.description
        if course_data.category_id is not None:
            # Validate category
            categor = await self.db.exec(select(Category).where(Category.id == course_data.category_id))
            category = categor.first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid category ID"
                )
            course.category_id = course_data.category_id
        if course_data.difficulty_level is not None:
            course.difficulty_level = course_data.difficulty_level
        if course_data.estimated_duration is not None:
            course.estimated_duration = course_data.estimated_duration
        if course_data.is_mandatory is not None:
            course.is_mandatory = course_data.is_mandatory
        if course_data.prerequisites is not None:
            # Validate prerequisites
            for prereq_id in course_data.prerequisites:
                prereq_courses = await self.db.exec(select(Course).where(Course.id == prereq_id))
                prereq_course = prereq_courses.first()
                if not prereq_course:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid prerequisite course ID: {prereq_id}"
                    )
            course.prerequisites = course_data.prerequisites
        if course_data.tags is not None:
            course.tags = course_data.tags
        if course_data.thumbnail_url is not None:
            course.thumbnail_url = course_data.thumbnail_url
        
        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course) 


        await  audit_service.log_update(
        db= self.db,
        user_id= current_user.get("sub"), 
        entity_type= course.__tablename__,
        entity_id=course.id,
        ip_address=request.client.host if request.client else None,
        details={"email": current_user.get("email")})
        
        return await self.get_course_by_id(course.id)
    
    async def publish_course(self, course_id: str) -> CourseDetailSchema:
        """Publish a course"""
        courses = await self.db.exec(select(Course).where(Course.id == course_id))
        course = courses.first()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        if course.status == CourseStatus.PUBLISHED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course is already published"
            )
        
        # Check if course has modules
        if not course.modules:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot publish course without modules"
            )
        
        course.status = CourseStatus.PUBLISHED
        course.published_at = datetime.utcnow()
        
        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)
        
        return await self.get_course_by_id(course.id)
    
    async def delete_course(self, request:Request,course_id: str,current_user:TokenData=Depends(access_token_bearer)) -> Dict[str, str]:
        """Delete a course"""
        courses = await self.db.exec(select(Course).where(Course.id == course_id))
        course = courses.first()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Check if course has enrollments
        if course.enrollments:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete course with existing enrollments"
            )
        
        self.db.delete(course)
        await self.db.commit() 

        await  audit_service.log_delete(
        db= self.db,
        user_id= current_user.get("sub"), 
        entity_type= course.__tablename__,
        entity_id= None,
        ip_address=request.client.host if request.client else None,
        details={"email": current_user.get("email")})
        
        return {"message": "Course deleted successfully"}
    
    # Category management methods
    async def get_categories(self, page: int = 1, limit: int = 20) -> PaginatedResponse[CategorySchema]:
        """Get paginated list of categories"""
        query = select(Category).order_by(Category.name)
        
        tota = await self.db.exec(select(func.count(Category.id)))
        total = tota.first()
        
        offset = (page - 1) * limit
        categorie = await self.db.exec(query.offset(offset).limit(limit))
        categories = categorie.all()
        
        category_schemas = []
        for category in categories:
            total_courses = len(category.courses)
            category_schemas.append(CategorySchema(
                id=category.id,
                name=category.name,
                description=category.description,
                parent_id=category.parent_id,
                color_code=category.color_code,
                total_courses=total_courses,
                created_at=category.created_at,
                updated_at=category.updated_at
            ))
        
        return PaginatedResponse.create(category_schemas, total, page, limit)
    
    async def create_category(self, category_data: CategoryCreateSchema) -> CategorySchema:
        """Create a new category"""
        # Check if category name already exists
        existing_categor = await self.db.exec(
            select(Category).where(Category.name == category_data.name)
        )
        existing_category = existing_categor.first()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists"
            )
        
        # Validate parent category if provided
        if category_data.parent_id:
            parent_categor = await self.db.exec(
                select(Category).where(Category.id == category_data.parent_id)
            )
            parent_category = parent_categor.first()
            if not parent_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid parent category ID"
                )
        
        new_category = Category(
            name=category_data.name,
            description=category_data.description,
            parent_id=category_data.parent_id,
            color_code=category_data.color_code
        )
        
        self.db.add(new_category)
        await self.db.commit()
        await self.db.refresh(new_category)
        
        return CategorySchema(
            id=new_category.id,
            name=new_category.name,
            description=new_category.description,
            parent_id=new_category.parent_id,
            color_code=new_category.color_code,
            total_courses=0,
            created_at=new_category.created_at,
            updated_at=new_category.updated_at
        )
    
    # Enrollment management methods
    async def enroll_user(self, enrollment_data: EnrollmentCreateSchema, assigned_by: Optional[str] = None) -> EnrollmentSchema:
        """Enroll a user in a course"""
        # Check if user exists
        users = await self.db.exec(select(User).where(User.id == enrollment_data.user_id))
        user = users.first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if course exists
        courses = await self.db.exec(select(Course).where(Course.id == enrollment_data.course_id))
        course = courses.first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Check if user is already enrolled
        existing_enrollments = await self.db.exec(
            select(Enrollment).where(
                (Enrollment.user_id == enrollment_data.user_id) &
                (Enrollment.course_id == enrollment_data.course_id)
            )
        )
        existing_enrollment = existing_enrollments.first()
        
        if existing_enrollment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already enrolled in this course"
            )
        
        # Create enrollment
        new_enrollment = Enrollment(
            user_id=enrollment_data.user_id,
            course_id=enrollment_data.course_id,
            enrolled_at=datetime.utcnow(),
            due_date=enrollment_data.due_date,
            assigned_by=assigned_by,
            status=EnrollmentStatus.ENROLLED
        )
        
        self.db.add(new_enrollment)
        await self.db.commit()
        await self.db.refresh(new_enrollment)
        
        # Send enrollment email
        await self.email_service.send_course_assignment_email(
            user.email,
            user.full_name,
            course.title,
            enrollment_data.due_date.strftime("%Y-%m-%d") if enrollment_data.due_date else None
        )
        
        return EnrollmentSchema(
            id=new_enrollment.id,
            user_id=new_enrollment.user_id,
            course_id=new_enrollment.course_id,
            enrolled_at=new_enrollment.enrolled_at,
            started_at=new_enrollment.started_at,
            completed_at=new_enrollment.completed_at,
            progress_percentage=new_enrollment.progress_percentage,
            status=new_enrollment.status,
            assigned_by=new_enrollment.assigned_by,
            due_date=new_enrollment.due_date,
            user_name=user.full_name,
            course_title=course.title,
            created_at=new_enrollment.created_at,
            updated_at=new_enrollment.updated_at
        )
    
    async def bulk_enroll_users(self, bulk_data: BulkEnrollmentSchema, assigned_by: Optional[str] = None) -> Dict[str, Any]:
        """Enroll multiple users in a course"""
        successful_enrollments = []
        failed_enrollments = []
        
        for user_id in bulk_data.user_ids:
            try:
                enrollment_data = EnrollmentCreateSchema(
                    user_id=user_id,
                    course_id=bulk_data.course_id,
                    due_date=bulk_data.due_date
                )
                enrollment =await self.enroll_user(enrollment_data, assigned_by)
                successful_enrollments.append(enrollment)
            except Exception as e:
                failed_enrollments.append({
                    "user_id": user_id,
                    "error": str(e)
                })
        
        return {
            "successful_enrollments": len(successful_enrollments),
            "failed_enrollments": len(failed_enrollments),
            "failures": failed_enrollments
        }
    
    async def get_course_stats(self) -> CourseStatsSchema:
        """Get course statistics"""
        total_course = await self.db.exec(select(func.count(Course.id)))
        total_courses = total_course.first()
        published_course =await  self.db.exec(
            select(func.count(Course.id)).where(Course.status == CourseStatus.PUBLISHED)
        )
        published_courses = published_course.first()
        draft_course = await self.db.exec(
            select(func.count(Course.id)).where(Course.status == CourseStatus.DRAFT)
        )
        draft_courses = draft_course.first()
        
        # Courses by category
        courses_by_categor = await self.db.exec(
            select(Category.name, func.count(Course.id))
            .join(Course, Course.category_id == Category.id)
            .group_by(Category.name)
        )
        courses_by_category = courses_by_categor.all()
        
        # Courses by difficulty
        courses_by_difficult = await self.db.exec(
            select(Course.difficulty_level, func.count(Course.id))
            .group_by(Course.difficulty_level)
        )
        courses_by_difficulty = courses_by_difficult.all()
        
        # Most popular courses (by enrollment count)
        most_popular_course = await self.db.exec(
            select(Course.title, func.count(Enrollment.id))
            .join(Enrollment, Enrollment.course_id == Course.id, isouter=True)
            .group_by(Course.id, Course.title)
            .order_by(func.count(Enrollment.id).desc())
            .limit(10)
        )
        most_popular_courses = most_popular_course.all()
        
        return CourseStatsSchema(
            total_courses=total_courses or 0,
            published_courses=published_courses or 0,
            draft_courses=draft_courses or 0,
            courses_by_category=[
                {"category": cat, "count": count} 
                for cat, count in courses_by_category
            ],
            courses_by_difficulty=[
                {"difficulty": diff.value, "count": count} 
                for diff, count in courses_by_difficulty
            ],
            most_popular_courses=[
                {"title": title, "enrollments": count} 
                for title, count in most_popular_courses
            ]
        )

