from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://waf_user:waf_password@localhost:5432/waf_db"
    
    # Admin
    ADMIN_PASSWORD: str = "admin123"
    SECRET_KEY: str = "your-secret-key-change-this"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    MAX_REQUEST_SIZE: int = 10485760  # 10MB
    BLOCKED_IP_RETENTION_DAYS: int = 30
    LOG_RETENTION_DAYS: int = 90
    
    # Rate Limiting
    DEFAULT_RATE_LIMIT: int = 1000
    DEFAULT_RATE_WINDOW: int = 3600
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "/app/logs/waf.log"
    
    class Config:
        env_file = ".env"

settings = Settings()
