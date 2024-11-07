from pydantic_settings import BaseSettings
from typing import Optional
import secrets

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Security
    JWT_SECRET: str = secrets.token_urlsafe(32)
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Firebase
    FIREBASE_PROJECT_ID: str
    FIREBASE_PRIVATE_KEY: str
    FIREBASE_CLIENT_EMAIL: str
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 104857600  # 100MB in bytes
    ALLOWED_FILE_TYPES: str = "video/*,application/pdf,application/epub+zip"
    STORAGE_BUCKET: str
    
    # Computed Properties
    @property
    def allowed_origins_list(self) -> list[str]:
        return self.ALLOWED_ORIGINS.split(",")
    
    @property
    def allowed_file_types_list(self) -> list[str]:
        return self.ALLOWED_FILE_TYPES.split(",")
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Validate settings
def validate_settings():
    """Validate critical settings on startup"""
    assert settings.DATABASE_URL, "DATABASE_URL is required"
    assert settings.FIREBASE_PROJECT_ID, "FIREBASE_PROJECT_ID is required"
    assert settings.FIREBASE_PRIVATE_KEY, "FIREBASE_PRIVATE_KEY is required"
    assert settings.FIREBASE_CLIENT_EMAIL, "FIREBASE_CLIENT_EMAIL is required"
    assert settings.STORAGE_BUCKET, "STORAGE_BUCKET is required"
    assert settings.MAX_UPLOAD_SIZE > 0, "MAX_UPLOAD_SIZE must be positive"
    assert len(settings.allowed_origins_list) > 0, "At least one origin must be allowed"
    assert len(settings.allowed_file_types_list) > 0, "At least one file type must be allowed"
    
    # Validate environment
    assert settings.ENVIRONMENT.lower() in ["development", "production"], \
        "ENVIRONMENT must be either 'development' or 'production'"
