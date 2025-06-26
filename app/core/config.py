"""
Application Configuration
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = ConfigDict(extra='ignore')
    
    # Application
    APP_NAME: str = "LMS Backend API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
     
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str 
    DB_HOST: str 
    DB_PORT: int
    DB_USER: str 
    DB_PASSWORD: str 
    DB_NAME: str 
    SECRET_KEY: str 
    ALGORITHM: str
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Email Configuration
    ELASTICMAIL_FROM_EMAIL: str 
    ELASTICMAIL_FROM_NAME: str
    ELASTICMAIL_API_KEY: str    
    
    
    # Redis (for caching and sessions)
    REDIS_URL: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO" 
    
    # URL 
    BASE_URL: str 
    API_V1_STR: str = "/api"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Construct PostgreSQL URL if individual components are provided
        if (self.DB_HOST and self.DB_USER and self.DB_PASSWORD and self.DB_NAME 
            and not self.DATABASE_URL.startswith("postgresql")):
            self.DATABASE_URL = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)


# Create settings instance
settings = Settings()

