import os
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Project"
    
    # Database
    DATABASE_URL: str = Field(
        default=os.getenv("DATABASE_URL"), 
        description="Database connection string"
    )
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    # JWT
    SECRET_KEY: str = Field(
        default=os.getenv("SECRET_KEY"), 
        description="Secret key for JWT token"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

settings = Settings() 