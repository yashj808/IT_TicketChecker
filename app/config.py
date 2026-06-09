import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "IT Ticket Classifier"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///./data/sqlite.db"
    
    # Environment config
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
