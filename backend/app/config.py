from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost/study_scheduler"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Redis for Celery
    redis_url: str = "redis://localhost:6379"
    
    # Email settings (for notifications)
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Frontend URL
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"


settings = Settings()
