import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database - Supabase PostgreSQL
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/tutor_system"
    
    # Supabase Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    
    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External Services
    HCMUT_SSO_URL: str = "http://localhost:3001"
    HCMUT_DATACORE_URL: str = "http://localhost:3002"
    HCMUT_LIBRARY_URL: str = "http://localhost:3003"
    AI_RECOMMENDER_URL: str = "http://localhost:3004"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "HCMUT Tutor Support System"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:80"
    CORS_ALLOW_CREDENTIALS: bool = True
    
    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()