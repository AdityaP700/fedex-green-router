from typing import Any, Optional, Union
import json
from datetime import datetime, timedelta
import aioredis
from config.settings import Settings

class CacheManager:
    def __init__(self, settings: Settings):
        self.redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Default TTLs for different types of data
        self.ttls = {
            "route": timedelta(hours=1),
            "weather": timedelta(minutes=30),
            "traffic": timedelta(minutes=5),
            "air_quality": timedelta(minutes=15),
            "user_preferences": timedelta(days=1),
            "vehicle": timedelta(hours=12),
            "ml_prediction": timedelta(minutes=10)
        }
    
    async def get(
        self,
        key: str,
        data_type: str = None
    ) -> Optional[Union[dict, list, str, int, float]]:
        """Get value from cache."""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Union[dict, list, str, int, float],
        data_type: str = None,
        ttl: Optional[timedelta] = None
    ):
        """Set value in cache with optional TTL."""
        try:
            # Use type-specific TTL if not provided
            if ttl is None and data_type in self.ttls:
                ttl = self.ttls[data_type]
            
            # Convert value to JSON string
            json_value = json.dumps(value)
            
            if ttl:
                await self.redis.set(key, json_value, ex=int(ttl.total_seconds()))
            else:
                await self.redis.set(key, json_value)
        except Exception as e:
            print(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete value from cache."""
        try:
            await self.redis.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")
    
    async def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern."""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
    
    async def get_route_cache(self, start_point: tuple, end_point: tuple) -> Optional[dict]:
        """Get cached route data."""
        key = f"route:{start_point[0]},{start_point[1]}:{end_point[0]},{end_point[1]}"
        return await self.get(key, "route")
    
    async def set_route_cache(
        self,
        start_point: tuple,
        end_point: tuple,
        route_data: dict
    ):
        """Cache route data."""
        key = f"route:{start_point[0]},{start_point[1]}:{end_point[0]},{end_point[1]}"
        await self.set(key, route_data, "route")
    
    async def get_weather_cache(self, lat: float, lon: float) -> Optional[dict]:
        """Get cached weather data."""
        key = f"weather:{lat},{lon}"
        return await self.get(key, "weather")
    
    async def set_weather_cache(self, lat: float, lon: float, weather_data: dict):
        """Cache weather data."""
        key = f"weather:{lat},{lon}"
        await self.set(key, weather_data, "weather")
    
    async def get_traffic_cache(self, start_point: tuple, end_point: tuple) -> Optional[dict]:
        """Get cached traffic data."""
        key = f"traffic:{start_point[0]},{start_point[1]}:{end_point[0]},{end_point[1]}"
        return await self.get(key, "traffic")
    
    async def set_traffic_cache(
        self,
        start_point: tuple,
        end_point: tuple,
        traffic_data: dict
    ):
        """Cache traffic data."""
        key = f"traffic:{start_point[0]},{start_point[1]}:{end_point[0]},{end_point[1]}"
        await self.set(key, traffic_data, "traffic")
    
    async def get_air_quality_cache(self, lat: float, lon: float) -> Optional[dict]:
        """Get cached air quality data."""
        key = f"aqi:{lat},{lon}"
        return await self.get(key, "air_quality")
    
    async def set_air_quality_cache(self, lat: float, lon: float, aqi_data: dict):
        """Cache air quality data."""
        key = f"aqi:{lat},{lon}"
        await self.set(key, aqi_data, "air_quality")
    
    async def get_user_preferences_cache(self, user_id: str) -> Optional[dict]:
        """Get cached user preferences."""
        key = f"preferences:{user_id}"
        return await self.get(key, "user_preferences")
    
    async def set_user_preferences_cache(self, user_id: str, preferences: dict):
        """Cache user preferences."""
        key = f"preferences:{user_id}"
        await self.set(key, preferences, "user_preferences")
    
    async def get_vehicle_cache(self, vehicle_id: str) -> Optional[dict]:
        """Get cached vehicle data."""
        key = f"vehicle:{vehicle_id}"
        return await self.get(key, "vehicle")
    
    async def set_vehicle_cache(self, vehicle_id: str, vehicle_data: dict):
        """Cache vehicle data."""
        key = f"vehicle:{vehicle_id}"
        await self.set(key, vehicle_data, "vehicle")
    
    async def get_ml_prediction_cache(
        self,
        model_type: str,
        feature_hash: str
    ) -> Optional[dict]:
        """Get cached ML prediction."""
        key = f"ml_prediction:{model_type}:{feature_hash}"
        return await self.get(key, "ml_prediction")
    
    async def set_ml_prediction_cache(
        self,
        model_type: str,
        feature_hash: str,
        prediction: dict
    ):
        """Cache ML prediction."""
        key = f"ml_prediction:{model_type}:{feature_hash}"
        await self.set(key, prediction, "ml_prediction")
    
    async def invalidate_route_cache(self, start_point: tuple, end_point: tuple):
        """Invalidate route cache."""
        key = f"route:{start_point[0]},{start_point[1]}:{end_point[0]},{end_point[1]}"
        await self.delete(key)
    
    async def invalidate_area_cache(self, lat: float, lon: float, radius: float):
        """Invalidate all cache entries in a geographical area."""
        # This is a simplified version. In a real system, you'd need more
        # sophisticated geospatial indexing.
        patterns = [
            f"weather:{lat}*",
            f"aqi:{lat}*",
            f"traffic:*{lat}*",
            f"route:*{lat}*"
        ]
        for pattern in patterns:
            await self.clear_pattern(pattern)
    
    async def clear_all_cache(self):
        """Clear all cache entries."""
        try:
            await self.redis.flushdb()
        except Exception as e:
            print(f"Clear all cache error: {e}")
    
    async def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        try:
            info = await self.redis.info()
            return {
                "used_memory": info["used_memory"],
                "used_memory_peak": info["used_memory_peak"],
                "total_keys": await self.redis.dbsize(),
                "hit_rate": info.get("keyspace_hits", 0) / (
                    info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1)
                ) * 100
            }
        except Exception as e:
            print(f"Get cache stats error: {e}")
            return {} 