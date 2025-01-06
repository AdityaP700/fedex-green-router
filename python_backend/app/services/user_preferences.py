from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class RoutePreferenceType(str, Enum):
    """Types of route preferences."""
    ECO_FRIENDLY = "eco_friendly"
    SPEED = "speed"
    COST_EFFECTIVE = "cost_effective"
    EV_FRIENDLY = "ev_friendly"
    AVOID_TOLLS = "avoid_tolls"
    AVOID_HIGHWAYS = "avoid_highways"
    SCENIC_ROUTE = "scenic_route"

class WeatherPreference(str, Enum):
    """Weather-related preferences."""
    AVOID_SNOW = "avoid_snow"
    AVOID_RAIN = "avoid_rain"
    AVOID_EXTREME_WEATHER = "avoid_extreme_weather"
    ANY_WEATHER = "any_weather"

class TimePreference(str, Enum):
    """Time-related preferences."""
    AVOID_PEAK_HOURS = "avoid_peak_hours"
    FLEXIBLE_TIMING = "flexible_timing"
    STRICT_TIMING = "strict_timing"

class UserPreferences(BaseModel):
    """Model for user route preferences."""
    user_id: str = Field(..., description="Unique identifier for the user")
    route_preferences: List[RoutePreferenceType] = Field(
        default_factory=list,
        description="List of route preferences"
    )
    weather_preference: WeatherPreference = Field(
        default=WeatherPreference.ANY_WEATHER,
        description="Weather-related preference"
    )
    time_preference: TimePreference = Field(
        default=TimePreference.FLEXIBLE_TIMING,
        description="Time-related preference"
    )
    max_route_options: int = Field(
        default=3,
        description="Maximum number of route options to return"
    )
    preferred_vehicle_types: Optional[List[str]] = Field(
        default=None,
        description="Preferred vehicle types for routes"
    )
    eco_score_threshold: Optional[float] = Field(
        default=None,
        description="Minimum eco-score threshold for routes"
    )
    max_emissions_threshold: Optional[float] = Field(
        default=None,
        description="Maximum allowed emissions in kg CO2"
    )
    preferred_charging_networks: Optional[List[str]] = Field(
        default=None,
        description="Preferred EV charging networks"
    )

    class Config:
        use_enum_values = True

class PreferenceHandler:
    """Handler for managing user preferences."""
    
    @staticmethod
    def get_routing_factors(preferences: UserPreferences) -> dict:
        """Convert user preferences to routing factors."""
        factors = {
            "eco_friendly": False,
            "speed_priority": False,
            "avoid_tolls": False,
            "avoid_highways": False,
            "weight_factors": {
                "distance": 1.0,
                "time": 1.0,
                "emissions": 1.0,
                "cost": 1.0
            }
        }
        
        for pref in preferences.route_preferences:
            if pref == RoutePreferenceType.ECO_FRIENDLY:
                factors["eco_friendly"] = True
                factors["weight_factors"]["emissions"] = 2.0
            elif pref == RoutePreferenceType.SPEED:
                factors["speed_priority"] = True
                factors["weight_factors"]["time"] = 2.0
            elif pref == RoutePreferenceType.COST_EFFECTIVE:
                factors["weight_factors"]["cost"] = 2.0
            elif pref == RoutePreferenceType.AVOID_TOLLS:
                factors["avoid_tolls"] = True
            elif pref == RoutePreferenceType.AVOID_HIGHWAYS:
                factors["avoid_highways"] = True
        
        # Adjust for weather preferences
        if preferences.weather_preference != WeatherPreference.ANY_WEATHER:
            factors["weather_sensitivity"] = 1.5
        
        # Adjust for time preferences
        if preferences.time_preference == TimePreference.AVOID_PEAK_HOURS:
            factors["avoid_peak_hours"] = True
        elif preferences.time_preference == TimePreference.STRICT_TIMING:
            factors["weight_factors"]["time"] *= 1.5
        
        return factors

    @staticmethod
    def validate_preferences(preferences: UserPreferences) -> bool:
        """Validate user preferences for consistency."""
        # Check for conflicting preferences
        if (RoutePreferenceType.SPEED in preferences.route_preferences and
            RoutePreferenceType.ECO_FRIENDLY in preferences.route_preferences):
            return False
        
        # Validate thresholds
        if preferences.eco_score_threshold is not None and (
            preferences.eco_score_threshold < 0 or preferences.eco_score_threshold > 100
        ):
            return False
        
        if preferences.max_emissions_threshold is not None and preferences.max_emissions_threshold < 0:
            return False
        
        return True

    @staticmethod
    def merge_preferences(base_prefs: UserPreferences, override_prefs: UserPreferences) -> UserPreferences:
        """Merge two sets of preferences, with override_prefs taking precedence."""
        merged_dict = base_prefs.dict()
        override_dict = override_prefs.dict()
        
        for key, value in override_dict.items():
            if value is not None:  # Only override non-None values
                merged_dict[key] = value
        
        return UserPreferences(**merged_dict) 