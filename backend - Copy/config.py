from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Fallback to local sqlite file
    DATABASE_URL: str = "sqlite:///./oilcast.db"
    REDIS_URL: str = "" # Not used in option 2 setup
    
    class Config:
        env_file = "../.env"
        extra = "ignore"

settings = Settings()
