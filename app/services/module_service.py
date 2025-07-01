"""
Module service for content management operations
"""
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from fastapi import HTTPException, status, UploadFile,Depends,Request
from datetime import datetime
import os
import uuid

from app.models.models.module import Module, Document, ContentType, VideoType
from app.models.models.module import Video
from app.models.models.course import Course
from app.schemas.module import (
    ModuleCreateSchema, ModuleUpdateSchema, ModuleResponseSchema, ModuleDetailSchema,
    DocumentCreateSchema, DocumentSchema, VideoCreateSchema, VideoUpdateSchema,
    VideoSchema, VideoProgressUpdateSchema, FileUploadResponseSchema
)
from app.schemas.base import PaginatedResponse
from app.core.config import settings 
from app.core.security import access_token_bearer 
from app.schemas.auth import TokenData 
from app.utils.audit import audit_service


class ModuleService:
    """Module and content management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_modules_by_course(self, course_id: str, page: int = 1, limit: int = 20) -> PaginatedResponse[ModuleResponseSchema]:
        """Get modules for a specific course"""
        # Verify course exists
        courses = await self.db.exec(select(Course).where(Course.id == course_id))
        course = courses.first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        query = select(Module).where(Module.course_id == course_id).order_by(Module.order_index)
        
        tota = await self.db.exec(select(func.count(Module.id)).where(Module.course_id == course_id))
        total = tota.first()
        
        offset = (page - 1) * limit
        moduless = await self.db.exec(query.offset(offset).limit(limit))
        modules = moduless.all()
        
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
    
    async def get_module_by_id(self, module_id: str, user_id: Optional[str] = None) -> ModuleDetailSchema:
        """Get module by ID with detailed information"""
        modules= await self.db.exec(select(Module).where(Module.id == module_id))
        module = modules.first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        # Get course information
        courses = await self.db.exec(select(Course).where(Course.id == module.course_id))
        course = courses.first()
        
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
    
    async def create_module(self, course_id: str,request:Request, module_data: ModuleCreateSchema,current_user:TokenData=Depends(access_token_bearer)) -> ModuleDetailSchema:
        """Create a new module"""
        # Verify course exists
        courses = await self.db.exec(select(Course).where(Course.id == course_id))
        course = courses.first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Get next order index if not provided
        if module_data.order_index == 0:
            max_orders = await self.db.exec(
                select(func.max(Module.order_index)).where(Module.course_id == course_id)
            )
            max_order = max_orders.first()
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
        await self.db.commit()
        await self.db.refresh(new_module) 


        await  audit_service.log_create(
        db= self.db,
        user_id= current_user.get("sub"), 
        entity_type= new_module.__tablename__,
        entity_id=new_module.id,
        ip_address=request.client.host if request.client else None,
        details={"email": current_user.get("email")})
        
        return await self.get_module_by_id(new_module.id)
    
    async def update_module(self, module_id: str,request:Request, module_data: ModuleUpdateSchema,current_user:TokenData=Depends(access_token_bearer)) -> ModuleDetailSchema:
        """Update module information"""
        modules = await self.db.exec(select(Module).where(Module.id == module_id))
        module = modules.first()
        
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
        await self.db.commit()
        await self.db.refresh(module) 


        await  audit_service.log_update(
        db= self.db,
        user_id= current_user.get("sub"), 
        entity_type= module.__tablename__,
        entity_id=module.id,
        ip_address=request.client.host if request.client else None,
        details={"email": current_user.get("email")})
        
        return await self.get_module_by_id(module.id)
    
    async def delete_module(self, request:Request,module_id: str,current_user:TokenData=Depends(access_token_bearer)) -> Dict[str, str]:
        """Delete a module"""
        modules = await self.db.exec(select(Module).where(Module.id == module_id))
        module = modules.first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        self.db.delete(module)
        await self.db.commit() 

        await  audit_service.log_delete(
        db= self.db,
        user_id= current_user.get("sub"), 
        entity_type= module.__tablename__,
        entity_id=None,
        ip_address=request.client.host if request.client else None,
        details={"email": current_user.get("email")})
        
        return {"message": "Module deleted successfully"}
    
    # Document management methods
    async def add_document_to_module(self, module_id: str, document_data: DocumentCreateSchema, file_path: str, file_size: int) -> DocumentSchema:
        """Add a document to a module"""
        modules = await self.db.exec(select(Module).where(Module.id == module_id))
        module = modules.first()
        
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
        await self.db.commit()
        await self.db.refresh(new_document)
        
        return new_document
    
    async def get_module_documents(self, module_id: str) -> List[DocumentSchema]:
        """Get all documents for a module"""
        modules = await  self.db.exec(select(Module).where(Module.id == module_id))
        module = modules.first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        document = await self.db.exec(select(Document).where(Document.module_id == module_id))
        documents = document.all()
        
        return documents
    
    async def delete_document(self, document_id: str) -> Dict[str, str]:
        """Delete a document"""
        documents = await self.db.exec(select(Document).where(Document.id == document_id))
        document = documents.first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Delete file from storage
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        self.db.delete(document)
        await self.db.commit()
        
        return {"message": "Document deleted successfully"}
    
    # Video management methods
    async def add_video_to_module(self, module_id: str, video_data: VideoCreateSchema) -> VideoSchema:
        """Add a video to a module"""
        modules = await self.db.exec(select(Module).where(Module.id == module_id))
        module = modules.first()
        
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
        await self.db.commit()
        await self.db.refresh(new_video)
        
        return new_video
    
    async def update_video(self, video_id: str, video_data: VideoUpdateSchema) -> VideoSchema:
        """Update video information"""
        videos = await self.db.exec(select(Video).where(Video.id == video_id))
        video = videos.first()
        
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
        await self.db.commit()
        await self.db.refresh(video)
        
        return video
    
    async def get_module_videos(self, module_id: str) -> List[VideoSchema]:
        """Get all videos for a module"""
        modules = await self.db.exec(select(Module).where(Module.id == module_id))
        module = modules.first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        
        video = await self.db.exec(select(Video).where(Video.module_id == module_id))
        videos = video.all()
        
        return videos
    
    async def delete_video(self, video_id: str) -> Dict[str, str]:
        """Delete a video"""
        videos = await self.db.exec(select(Video).where(Video.id == video_id))
        video = videos.first()
        
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        
        self.db.delete(video)
        await self.db.commit()
        
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
    
    async def reorder_modules(self, course_id: str, module_orders: List[Dict[str, int]]) -> Dict[str, str]:
        """Reorder modules in a course"""
        courses = await self.db.exec(select(Course).where(Course.id == course_id))
        course = courses.first()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Update module orders
        for order_data in module_orders:
            module_id = order_data.get("module_id")
            new_order = order_data.get("order_index")
            
            modules = await self.db.exec(select(Module).where(Module.id == module_id))
            module = modules.first()
            if module and module.course_id == course_id:
                module.order_index = new_order
                self.db.add(module)
        
        await self.db.commit()
        
        return {"message": "Modules reordered successfully"}

