from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Fallback to local sqlite file (use /app/data in Docker for persistence)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./oilcast.db")
    REDIS_URL: str = "" # Not used in option 2 setup
    
    class Config:
        env_file = "../.env"
        extra = "ignore"

settings = Settings()
