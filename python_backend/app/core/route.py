from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from .location import Location

class Route(BaseModel):
    """Model representing a route."""
    id: str
    start_location: Location
    end_location: Location
    waypoints: List[Location] = Field(default_factory=list)
    vehicle_id: str
    load_weight: float = Field(..., gt=0)
    departure_time: datetime
    total_distance: float = Field(..., gt=0)
    total_duration: float = Field(..., gt=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict) 