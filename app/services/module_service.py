"""
Module service for content management operations
"""
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from fastapi import HTTPException, status, UploadFile
from datetime import datetime
import os
import uuid

from app.models.models.module import Module, Document, Video, ContentType, VideoType
from app.models.models.course import Course
from app.schemas.module import (
    ModuleCreateSchema, ModuleUpdateSchema, ModuleResponseSchema, ModuleDetailSchema,
    DocumentCreateSchema, DocumentSchema, VideoCreateSchema, VideoUpdateSchema,
    VideoSchema, VideoProgressUpdateSchema, FileUploadResponseSchema
)
from app.schemas.base import PaginatedResponse
from app.core.config import settings


class ModuleService:
    """Module and content management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_modules_by_course(self, course_id: str, page: int = 1, limit: int = 20) -> PaginatedResponse[ModuleResponseSchema]:
        """Get modules for a specific course"""
        # Verify course exists
        course = self.db.exec(select(Course).where(Course.id == course_id)).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        query = select(Module).where(Module.course_id == course_id).order_by(Module.order_index)
        
        total = self.db.exec(select(func.count(Module.id)).where(Module.course_id == course_id)).first()
        
        offset = (page - 1) * limit
        modules = self.db.exec(query.offset(offset).limit(limit)).all()
        
        module_schemas = []
        for module in modules:
            # Check for related content
            has_quiz = len(module.quizzes) > 0
            has_video = len(module.videos) > 0
            has_documents = len(module.documents) > 0
            
            module_schemas.append(ModuleResponseSchema(
                id=module.id,
                course_id=module.course_id,
                title=module.title,
                description=module.description,
                content_type=module.content_type,
                content_url=module.content_url,
                content_data=module.content_data,
                order_index=module.order_index,
                is_mandatory=module.is_mandatory,
                estimated_duration=module.estimated_duration,
                has_quiz=has_quiz,
                has_video=has_video,
                has_documents=has_documents,
                created_at=module.created_at,
                updated_at=module.updated_at
            ))
        
        return PaginatedResponse.create(module_schemas, total, page, limit)
    
    def get_module_by_id(self, module_id: str, user_id: Optional[str] = None) -> ModuleDetailSchema:
        """Get module by ID with detailed information"""
        module = self.db.exec(select(Module).where(Module.id == module_id)).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        # Get course information
        course = self.db.exec(select(Course).where(Course.id == module.course_id)).first()
        
        # Get related content
        documents = [
            DocumentSchema.model_validate(doc) for doc in module.documents
        ]
        
        videos = [
            VideoSchema.model_validate(video) for video in module.videos
        ]
        
        # Get quizzes (placeholder - will be implemented with quiz service)
        quizzes = []
        
        # Get user progress if user_id provided
        user_progress = None
        if user_id:
            # This would be implemented with progress service
            pass
        
        return ModuleDetailSchema(
            id=module.id,
            course_id=module.course_id,
            course_title=course.title if course else "Unknown",
            title=module.title,
            description=module.description,
            content_type=module.content_type,
            content_url=module.content_url,
            content_data=module.content_data,
            order_index=module.order_index,
            is_mandatory=module.is_mandatory,
            estimated_duration=module.estimated_duration,
            documents=documents,
            videos=videos,
            quizzes=quizzes,
            user_progress=user_progress,
            created_at=module.created_at,
            updated_at=module.updated_at
        )
    
    def create_module(self, course_id: str, module_data: ModuleCreateSchema) -> ModuleDetailSchema:
        """Create a new module"""
        # Verify course exists
        course = self.db.exec(select(Course).where(Course.id == course_id)).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Get next order index if not provided
        if module_data.order_index == 0:
            max_order = self.db.exec(
                select(func.max(Module.order_index)).where(Module.course_id == course_id)
            ).first()
            module_data.order_index = (max_order or 0) + 1
        
        # Create new module
        new_module = Module(
            course_id=course_id,
            title=module_data.title,
            description=module_data.description,
            content_type=module_data.content_type,
            content_url=module_data.content_url,
            content_data=module_data.content_data,
            order_index=module_data.order_index,
            is_mandatory=module_data.is_mandatory,
            estimated_duration=module_data.estimated_duration
        )
        
        self.db.add(new_module)
        self.db.commit()
        self.db.refresh(new_module)
        
        return self.get_module_by_id(new_module.id)
    
    def update_module(self, module_id: str, module_data: ModuleUpdateSchema) -> ModuleDetailSchema:
        """Update module information"""
        module = self.db.exec(select(Module).where(Module.id == module_id)).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        # Update fields
        if module_data.title is not None:
            module.title = module_data.title
        if module_data.description is not None:
            module.description = module_data.description
        if module_data.content_type is not None:
            module.content_type = module_data.content_type
        if module_data.content_url is not None:
            module.content_url = module_data.content_url
        if module_data.content_data is not None:
            module.content_data = module_data.content_data
        if module_data.order_index is not None:
            module.order_index = module_data.order_index
        if module_data.is_mandatory is not None:
            module.is_mandatory = module_data.is_mandatory
        if module_data.estimated_duration is not None:
            module.estimated_duration = module_data.estimated_duration
        
        self.db.add(module)
        self.db.commit()
        self.db.refresh(module)
        
        return self.get_module_by_id(module.id)
    
    def delete_module(self, module_id: str) -> Dict[str, str]:
        """Delete a module"""
        module = self.db.exec(select(Module).where(Module.id == module_id)).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        self.db.delete(module)
        self.db.commit()
        
        return {"message": "Module deleted successfully"}
    
    # Document management methods
    def add_document_to_module(self, module_id: str, document_data: DocumentCreateSchema, file_path: str, file_size: int) -> DocumentSchema:
        """Add a document to a module"""
        module = self.db.exec(select(Module).where(Module.id == module_id)).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        new_document = Document(
            module_id=module_id,
            title=document_data.title,
            file_path=file_path,
            file_type=document_data.file_type,
            file_size=file_size,
            is_downloadable=document_data.is_downloadable
        )
        
        self.db.add(new_document)
        self.db.commit()
        self.db.refresh(new_document)
        
        return DocumentSchema.model_validate(new_document)
    
    def get_module_documents(self, module_id: str) -> List[DocumentSchema]:
        """Get all documents for a module"""
        module = self.db.exec(select(Module).where(Module.id == module_id)).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        documents = self.db.exec(select(Document).where(Document.module_id == module_id)).all()
        
        return [DocumentSchema.model_validate(doc) for doc in documents]
    
    def delete_document(self, document_id: str) -> Dict[str, str]:
        """Delete a document"""
        document = self.db.exec(select(Document).where(Document.id == document_id)).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Delete file from storage
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        self.db.delete(document)
        self.db.commit()
        
        return {"message": "Document deleted successfully"}
    
    # Video management methods
    def add_video_to_module(self, module_id: str, video_data: VideoCreateSchema) -> VideoSchema:
        """Add a video to a module"""
        module = self.db.exec(select(Module).where(Module.id == module_id)).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        new_video = Video(
            module_id=module_id,
            title=video_data.title,
            video_url=video_data.video_url,
            duration=video_data.duration,
            thumbnail_url=video_data.thumbnail_url,
            video_type=video_data.video_type,
            quality_options=video_data.quality_options,
            subtitles_url=video_data.subtitles_url
        )
        
        self.db.add(new_video)
        self.db.commit()
        self.db.refresh(new_video)
        
        return VideoSchema.model_validate(new_video)
    
    def update_video(self, video_id: str, video_data: VideoUpdateSchema) -> VideoSchema:
        """Update video information"""
        video = self.db.exec(select(Video).where(Video.id == video_id)).first()
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        
        # Update fields
        if video_data.title is not None:
            video.title = video_data.title
        if video_data.video_url is not None:
            video.video_url = video_data.video_url
        if video_data.duration is not None:
            video.duration = video_data.duration
        if video_data.thumbnail_url is not None:
            video.thumbnail_url = video_data.thumbnail_url
        if video_data.video_type is not None:
            video.video_type = video_data.video_type
        if video_data.quality_options is not None:
            video.quality_options = video_data.quality_options
        if video_data.subtitles_url is not None:
            video.subtitles_url = video_data.subtitles_url
        
        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)
        
        return VideoSchema.model_validate(video)
    
    def get_module_videos(self, module_id: str) -> List[VideoSchema]:
        """Get all videos for a module"""
        module = self.db.exec(select(Module).where(Module.id == module_id)).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        videos = self.db.exec(select(Video).where(Video.module_id == module_id)).all()
        
        return [VideoSchema.model_validate(video) for video in videos]
    
    def delete_video(self, video_id: str) -> Dict[str, str]:
        """Delete a video"""
        video = self.db.exec(select(Video).where(Video.id == video_id)).first()
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        
        self.db.delete(video)
        self.db.commit()
        
        return {"message": "Video deleted successfully"}
    
    # File upload methods
    async def upload_file(self, file: UploadFile, upload_type: str = "document") -> FileUploadResponseSchema:
        """Upload a file and return file information"""
        # Validate file type
        allowed_extensions = {
            "document": [".pdf", ".doc", ".docx", ".ppt", ".pptx", ".txt"],
            "video": [".mp4", ".avi", ".mov", ".wmv", ".flv"],
            "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
        }
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions.get(upload_type, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type for {upload_type}. Allowed: {allowed_extensions.get(upload_type, [])}"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}{file_extension}"
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(settings.UPLOAD_DIR, upload_type)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        file_size = len(content)
        
        return FileUploadResponseSchema(
            file_id=file_id,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_extension[1:]  # Remove the dot
        )
    
    def reorder_modules(self, course_id: str, module_orders: List[Dict[str, int]]) -> Dict[str, str]:
        """Reorder modules in a course"""
        course = self.db.exec(select(Course).where(Course.id == course_id)).first()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Update module orders
        for order_data in module_orders:
            module_id = order_data.get("module_id")
            new_order = order_data.get("order_index")
            
            module = self.db.exec(select(Module).where(Module.id == module_id)).first()
            if module and module.course_id == course_id:
                module.order_index = new_order
                self.db.add(module)
        
        self.db.commit()
        
        return {"message": "Modules reordered successfully"}

