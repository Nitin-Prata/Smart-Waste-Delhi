"""
Configuration settings for Smart Waste & Air Quality Management System
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:Nitin%402004@localhost:5432/smartwaste"
    REDIS_URL: str = "redis://localhost:6379"
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    MAPBOX_API_KEY: Optional[str] = None
    WEATHER_API_KEY: Optional[str] = None
    
    # Air Quality APIs
    OPENAQ_API_URL: str = "https://api.openaq.org/v2"
    CPCB_API_URL: str = "https://api.cpcbccr.com"
    
    # IoT Configuration
    MQTT_BROKER: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    
    # AI Model Settings
    LSTM_MODEL_PATH: str = "models/lstm_air_quality.h5"
    RANDOM_FOREST_MODEL_PATH: str = "models/rf_waste_prediction.pkl"
    
    # Delhi Coordinates (approximate center)
    DELHI_CENTER_LAT: float = 28.7041
    DELHI_CENTER_LON: float = 77.1025
    
    # Air Quality Thresholds
    AQI_GOOD: int = 50
    AQI_MODERATE: int = 100
    AQI_UNHEALTHY_SENSITIVE: int = 150
    AQI_UNHEALTHY: int = 200
    AQI_VERY_UNHEALTHY: int = 300
    AQI_HAZARDOUS: int = 500
    
    # Waste Management Settings
    WASTE_COLLECTION_INTERVAL_HOURS: int = 24
    BIN_FILL_THRESHOLD: float = 0.8  # 80% full
    
    # Alert Settings
    ALERT_CHECK_INTERVAL_MINUTES: int = 15
    SMS_ENABLED: bool = False
    EMAIL_ENABLED: bool = True
    
    # Development
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings() 