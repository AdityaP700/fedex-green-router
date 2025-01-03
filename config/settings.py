from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MongoDB settings
    MONGODB_URI: str
    
    # Redis settings
    REDIS_URL: str
    
    # API Keys
    TOMTOM_API_KEY: str
    OPENWEATHER_API_KEY: str
    AQICN_API_KEY: str
    MAPMYINDIA_API_KEY: str
    VAHAN_API_KEY: Optional[str] = None
    
    # API Endpoints
    TOMTOM_BASE_URL: str = "https://api.tomtom.com/routing/1"
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    AQICN_BASE_URL: str = "https://api.waqi.info"
    
    # Security
    SECRET_KEY: str
    
    # Application Settings
    DEBUG: bool = False
    API_VERSION: str = "v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()