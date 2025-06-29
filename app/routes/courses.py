"""
Course management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query,Request
from sqlmodel import Session
from typing import Optional

from app.db.database import get_session
from app.services.course_service import CourseService
from app.schemas.course import (
    CourseListParams, CourseDetailSchema, CourseCreateSchema, CourseUpdateSchema,
    CourseStatsSchema, CategoryCreateSchema, CategoryUpdateSchema, CategorySchema,
    EnrollmentCreateSchema, EnrollmentUpdateSchema, EnrollmentSchema,
    EnrollmentListParams, BulkEnrollmentSchema, PaginatedCoursesResponse,
    PaginatedCategoriesResponse, PaginatedEnrollmentsResponse
)
from app.schemas.base import MessageResponse
from app.core.security import access_token_bearer
from app.schemas.auth import TokenData

router = APIRouter()


@router.get("/", response_model=PaginatedCoursesResponse)
async def get_courses(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    category_id: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    creator_id: Optional[str] = Query(None),
    is_mandatory: Optional[bool] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get paginated list of courses"""
    course_service = CourseService(db)
    params = CourseListParams(
        search=search,
        category_id=category_id,
        difficulty=difficulty,
        status=status,
        creator_id=creator_id,
        is_mandatory=is_mandatory,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return await course_service.get_courses(params, page, limit)


@router.post("/", response_model=CourseDetailSchema, status_code=status.HTTP_201_CREATED)
async def create_course( 
    request:Request,
    course_data: CourseCreateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Create a new course"""
    course_service = CourseService(db)
    id = current_user.get("sub")
    return await course_service.create_course(course_data, id,current_user,request)


@router.get("/stats", response_model=CourseStatsSchema)
async def get_course_stats(
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get course statistics"""
    course_service = CourseService(db)
    return await course_service.get_course_stats()


@router.get("/my-courses", response_model=PaginatedCoursesResponse)
async def get_my_courses(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get courses created by current user"""
    course_service = CourseService(db) 
    id = current_user.get("sub")
    params = CourseListParams(creator_id=id)
    return await course_service.get_courses(params, page, limit)


@router.get("/{course_id}", response_model=CourseDetailSchema)
async def get_course_by_id(
    course_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get course by ID"""
    course_service = CourseService(db) 
    id = current_user.get("sub")
    return await course_service.get_course_by_id(course_id, id)


@router.put("/{course_id}", response_model=CourseDetailSchema)
async def update_course( 
    request:Request,
    course_id: str,
    course_data: CourseUpdateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Update course information"""
    course_service = CourseService(db)
    return await course_service.update_course(course_id, course_data,current_user,request)


@router.post("/{course_id}/publish", response_model=CourseDetailSchema)
async def publish_course(
    course_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Publish a course"""
    course_service = CourseService(db)
    return course_service.publish_course(course_id)


@router.delete("/{course_id}", response_model=MessageResponse)
async def delete_course( 
    request:Request,
    course_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Delete a course"""
    course_service = CourseService(db)
    result = course_service.delete_course(course_id,current_user,request)
    return MessageResponse(message=result["message"])


# Category management endpoints
@router.get("/categories/", response_model=PaginatedCategoriesResponse)
async def get_categories(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get paginated list of categories"""
    course_service = CourseService(db)
    return course_service.get_categories(page, limit)


@router.post("/categories/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Create a new category"""
    course_service = CourseService(db)
    return course_service.create_category(category_data)


# Enrollment management endpoints
@router.post("/enroll", response_model=EnrollmentSchema, status_code=status.HTTP_201_CREATED)
async def enroll_user(
    enrollment_data: EnrollmentCreateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Enroll a user in a course"""
    course_service = CourseService(db)
    return await course_service.enroll_user(enrollment_data, current_user.username)


@router.post("/bulk-enroll", status_code=status.HTTP_201_CREATED)
async def bulk_enroll_users(
    bulk_data: BulkEnrollmentSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Enroll multiple users in a course"""
    course_service = CourseService(db)
    return await course_service.bulk_enroll_users(bulk_data, current_user.username)


@router.post("/{course_id}/enroll-me", response_model=EnrollmentSchema, status_code=status.HTTP_201_CREATED)
async def enroll_current_user(
    course_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Enroll current user in a course (self-enrollment)"""
    course_service = CourseService(db)
    enrollment_data = EnrollmentCreateSchema(
        user_id=current_user.username,
        course_id=course_id
    )
    return await course_service.enroll_user(enrollment_data)


# Create router instance for export
courses_router = router


