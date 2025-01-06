from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Vehicle(BaseModel):
    """Model representing a vehicle in the system."""
    id: Optional[str] = None
    vehicle_type: str
    registration_number: str
    max_load: float
    current_load: float = 0
    fuel_type: str
    fuel_efficiency: float
    emissions_factor: float
    status: str = "available"
    location: Dict[str, float] = Field(default_factory=dict)
    last_maintenance: Optional[datetime] = None
    maintenance_history: list = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "populate_by_name": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    } 