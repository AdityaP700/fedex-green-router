from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from error_handling.exceptions import ValidationError

class Location(BaseModel):
    """Location model with latitude and longitude."""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")

class RouteValidator(BaseModel):
    """Route request validation model."""
    start_location: Location
    end_location: Location
    vehicle_id: str
    load_weight: float = Field(..., gt=0, description="Load weight in kg")
    departure_time: datetime
    waypoints: Optional[List[Location]] = None

    @validator("load_weight")
    def validate_load_weight(cls, v: float) -> float:
        if v <= 0:
            raise ValidationError("Load weight must be positive")
        return v

    @validator("waypoints")
    def validate_waypoints(cls, v: Optional[List[Location]]) -> Optional[List[Location]]:
        if v and len(v) > 10:
            raise ValidationError("Maximum of 10 waypoints allowed")
        return v 