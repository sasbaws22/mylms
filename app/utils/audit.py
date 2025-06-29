from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime
from app.models.models.AuditLog import AuditLog,AuditAction
from app.schemas.audit import AuditLogCreate

class AuditService:
    @staticmethod
    async def log_action(
        db: AsyncSession,
        user_id: UUID,
        action: str,
        entity_type: str,
        entity_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        
    ) -> AuditLog:
        """
        Log an action in the audit trail
        
        Args:
            db: Database session
            user_id: ID of the user performing the action
            action: Type of action (from AuditAction)
            entity_type: Type of entity being acted upon
            entity_id: ID of the entity being acted upon
            details: Additional details about the action
            ip_address: IP address of the user
            
        Returns:
            Created AuditLog object
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
    
        )
        
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
        
        return audit_log
    
    @staticmethod
    async def log_create(
        db: AsyncSession,
        user_id: UUID,
        entity_type: str,
        entity_id: UUID,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Log a create action
        """
        return AuditService.log_action(
            db=db,
            user_id=user_id,
            action=AuditAction.CREATE,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address
        )
    
    @staticmethod
    def log_update(
        db:  AsyncSession,
        user_id: UUID,
        entity_type: str,
        entity_id: UUID,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Log an update action
        """
        return AuditService.log_action(
            db=db,
            user_id=user_id,
            action=AuditAction.UPDATE,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address
        )
    
    @staticmethod
    def log_delete(
        db: AsyncSession,
        user_id: UUID,
        entity_type: str,
        entity_id: UUID,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Log a delete action
        """
        return AuditService.log_action(
            db=db,
            user_id=user_id,
            action=AuditAction.DELETE,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address
        )
    
    @staticmethod
    def log_login(
        db: AsyncSession,
        user_id: UUID,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Log a login action
        """
        return AuditService.log_action(
            db=db,
            user_id=user_id,
            action=AuditAction.LOGIN,
            entity_type="User",
            entity_id=user_id,
            details=details,
            ip_address=ip_address
        )
    
     
audit_service = AuditService()
