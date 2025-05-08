import secrets
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
import os
from pathlib import Path

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # MongoDB settings
    MONGO_HOST: str = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT: int = int(os.getenv("MONGO_PORT", 27017))
    MONGO_USER: Optional[str] = os.getenv("MONGO_USER")
    MONGO_PASSWORD: Optional[str] = os.getenv("MONGO_PASSWORD")
    MONGO_DB: str = os.getenv("MONGO_DB", "oj_system")
    
    # Build MongoDB connection string
    @validator("MONGO_USER", "MONGO_PASSWORD")
    def check_mongo_credentials(cls, v, values, **kwargs):
        return v or ""
    
    @property
    def MONGO_CONNECTION_STRING(self) -> str:
        if self.MONGO_USER and self.MONGO_PASSWORD:
            return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}"
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    PROJECT_NAME: str = "Online Judge System"
    
    # Judge settings
    JUDGE_TIMEOUT: int = 10  # seconds
    JUDGE_MEMORY_LIMIT: int = 512  # MB
    
    # Storage paths
    PROBLEMS_DIR: Path = Path("/root/online-judge/problems")
    SUBMISSIONS_DIR: Path = Path("/root/online-judge/submissions")
    
    # LLM Integration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE: Optional[str] = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

# Create required directories
os.makedirs(settings.PROBLEMS_DIR, exist_ok=True)
os.makedirs(settings.SUBMISSIONS_DIR, exist_ok=True)
