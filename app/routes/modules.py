"""
Module and content management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File ,Request
from sqlmodel import Session
from typing import Optional, List

from app.db.database import get_session
from app.services.module_service import ModuleService
from app.schemas.module import (
    ModuleCreateSchema, ModuleUpdateSchema, ModuleResponseSchema, ModuleDetailSchema,
    DocumentCreateSchema, DocumentSchema, VideoCreateSchema, VideoUpdateSchema,
    VideoSchema, FileUploadResponseSchema, PaginatedModulesResponse
)
from app.schemas.base import MessageResponse
from app.core.security import access_token_bearer 
from app.schemas.auth import TokenData

router = APIRouter()


@router.get("/course/{course_id}", response_model=PaginatedModulesResponse)
async def get_modules_by_course(
    course_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get modules for a specific course"""
    module_service = ModuleService(db)
    return await module_service.get_modules_by_course(course_id, page, limit)


@router.post("/course/{course_id}", response_model=ModuleDetailSchema, status_code=status.HTTP_201_CREATED)
async def create_module( 
    request:Request,
    course_id: str,
    module_data: ModuleCreateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Create a new module in a course"""
    module_service = ModuleService(db)
    return await  module_service.create_module(course_id, module_data,current_user,request)


@router.get("/{module_id}", response_model=ModuleDetailSchema)
async def get_module_by_id(
    module_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get module by ID with detailed information"""
    module_service = ModuleService(db) 
    id = current_user.get("sub")
    return await  module_service.get_module_by_id(module_id, id)


@router.put("/{module_id}", response_model=ModuleDetailSchema)
async def update_module( 
    request:Request,
    module_id: str,
    module_data: ModuleUpdateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Update module information"""
    module_service = ModuleService(db) 

    return await module_service.update_module(module_id, module_data,current_user,request)


@router.delete("/{module_id}", response_model=MessageResponse)
async def delete_module( 
    request:Request,
    module_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Delete a module"""
    module_service = ModuleService(db)
    result = await  module_service.delete_module(module_id,request,current_user)
    return MessageResponse(message=result["message"])


# Document management endpoints
@router.get("/{module_id}/documents", response_model=List[DocumentSchema])
async def get_module_documents(
    module_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get all documents for a module"""
    module_service = ModuleService(db)
    return await  module_service.get_module_documents(module_id)


@router.post("/{module_id}/documents", response_model=DocumentSchema, status_code=status.HTTP_201_CREATED)
async def add_document_to_module(
    module_id: str,
    title: str,
    file_type: str,
    is_downloadable: bool = True,
    file: UploadFile = File(...),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Add a document to a module"""
    module_service = ModuleService(db)
    
    # Upload file first
    file_upload = await module_service.upload_file(file, "document")
    
    # Create document data
    document_data = DocumentCreateSchema(
        title=title,
        file_type=file_type,
        is_downloadable=is_downloadable
    )
    
    return await  module_service.add_document_to_module(
        module_id, 
        document_data, 
        file_upload.file_path, 
        file_upload.file_size
    )


@router.delete("/documents/{document_id}", response_model=MessageResponse)
async def delete_document(
    document_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Delete a document"""
    module_service = ModuleService(db)
    result = await module_service.delete_document(document_id)
    return MessageResponse(message=result["message"])


# Video management endpoints
@router.get("/{module_id}/videos", response_model=List[VideoSchema])
async def get_module_videos(
    module_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Get all videos for a module"""
    module_service = ModuleService(db)
    return await module_service.get_module_videos(module_id)


@router.post("/{module_id}/videos", response_model=VideoSchema, status_code=status.HTTP_201_CREATED)
async def add_video_to_module(
    module_id: str,
    video_data: VideoCreateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Add a video to a module"""
    module_service = ModuleService(db)
    return await module_service.add_video_to_module(module_id, video_data)


@router.put("/videos/{video_id}", response_model=VideoSchema)
async def update_video(
    video_id: str,
    video_data: VideoUpdateSchema,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Update video information"""
    module_service = ModuleService(db)
    return await module_service.update_video(video_id, video_data)


@router.delete("/videos/{video_id}", response_model=MessageResponse)
async def delete_video(
    video_id: str,
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Delete a video"""
    module_service = ModuleService(db)
    result = await module_service.delete_video(video_id)
    return MessageResponse(message=result["message"])


# File upload endpoints
@router.post("/upload", response_model=FileUploadResponseSchema)
async def upload_file(
    file: UploadFile = File(...),
    upload_type: str = Query("document", regex="^(document|video|image)$"),
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Upload a file"""
    module_service = ModuleService(db)
    return await module_service.upload_file(file, upload_type)


@router.post("/course/{course_id}/reorder", response_model=MessageResponse)
async def reorder_modules(
    course_id: str,
    module_orders: List[dict],
    current_user: TokenData = Depends(access_token_bearer),
    db: Session = Depends(get_session)
):
    """Reorder modules in a course"""
    module_service = ModuleService(db)
    result = await module_service.reorder_modules(course_id, module_orders)
    return MessageResponse(message=result["message"])


# Create router instance for export
modules_router = router


