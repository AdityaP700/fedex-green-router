from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class TrafficData(BaseModel):
    """Model for traffic data."""
    timestamp: datetime
    location: Dict[str, float]
    congestion_level: float
    speed: float
    raw_data: Dict[str, Any]

class WeatherData(BaseModel):
    """Model for weather data."""
    timestamp: datetime
    location: Dict[str, float]
    temperature: float
    humidity: float
    wind_speed: float
    precipitation: float
    raw_data: Dict[str, Any]

class AirQualityData(BaseModel):
    """Model for air quality data."""
    timestamp: datetime
    location: Dict[str, float]
    aqi: int
    pollutants: Dict[str, float]
    raw_data: Dict[str, Any] 