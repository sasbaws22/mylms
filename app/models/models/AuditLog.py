from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON, Text
import enum 
import uuid 
import sqlalchemy.dialects.postgresql as pg 




class AuditAction:
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"

class AuditLog(SQLModel,table=True):
    __tablename__ = "audit_logs"

    id  : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    user_id :Optional[uuid.UUID] =  Field( nullable=True, foreign_key="users.id",default=None)
    action:str = Field(nullable=False)
    entity_type:str = Field(nullable=False)
    entity_id :Optional[uuid.UUID] =  Field( nullable=True,default=None)
    details:str = Field(sa_column=Column(JSON, nullable=False))
    ip_address:str = Field(nullable=True)
    created_at:datetime= Field(default_factory=datetime.now)

    # Relationships
    user:User = Relationship(back_populates="audit_logs",sa_relationship_kwargs={"lazy": "selectin"})  




# Import other models to avoid circular imports
from app.models.models.user import User