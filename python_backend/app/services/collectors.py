from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import httpx
from config.settings import settings

class BaseDataCollector(ABC):
    """Base class for all data collectors."""
    
    @abstractmethod
    async def collect_data(self) -> Dict[str, Any]:
        """Collect data from the source."""
        pass

class TrafficDataCollector(BaseDataCollector):
    """Collector for traffic data from TomTom API."""
    
    async def collect_data(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.TOMTOM_BASE_URL}/traffic",
                params={"key": settings.TOMTOM_API_KEY}
            )
            return response.json()

class WeatherDataCollector(BaseDataCollector):
    """Collector for weather data from OpenWeather API."""
    
    async def collect_data(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.OPENWEATHER_BASE_URL}/weather",
                params={"appid": settings.OPENWEATHER_API_KEY}
            )
            return response.json()

class AirQualityDataCollector(BaseDataCollector):
    """Collector for air quality data from AQICN API."""
    
    async def collect_data(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AQICN_BASE_URL}/feed/here/",
                params={"token": settings.AQICN_API_KEY}
            )
            return response.json() 