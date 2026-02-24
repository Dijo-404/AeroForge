# src/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "mock-aeroforge-project-id")
    LOCATION: str = os.getenv("GCP_LOCATION", "us-central1")
    VERTEX_DATA_STORE_ID: str = os.getenv("VERTEX_DATA_STORE_ID", "mock-data-store-id")
    
    # ADK / Gemini Configuration
    GEMINI_MODEL: str = "gemini-2.5-pro"
    GEMINI_API_KEY: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
