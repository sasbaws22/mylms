"""
Application Configuration
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings,SettingsConfigDict



class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "LMS Backend API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
     
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str 
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
    
    # Logging
    LOG_LEVEL: str = "INFO" 
    
    # URL 
    BASE_URL: str 
    API_V1_STR: str = "/api"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
    
    model_config = SettingsConfigDict(
        
        env_file =".env",  
        extra ="ignore"    
    )

# Create settings instance
settings = Settings()

