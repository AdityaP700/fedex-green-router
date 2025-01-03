from pydantic import BaseModel, Field, validator
from typing import Dict, Any

class Preferences(BaseModel):
    """Model representing user preferences."""
    eco_priority: float = Field(..., ge=0, le=1)
    speed_priority: float = Field(..., ge=0, le=1)
    cost_priority: float = Field(..., ge=0, le=1)
    max_route_options: int = Field(default=1, ge=1, le=5)
    avoid_tolls: bool = Field(default=False)
    avoid_highways: bool = Field(default=False)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator("eco_priority", "speed_priority", "cost_priority")
    def validate_priorities(cls, v: float, values: Dict[str, Any]) -> float:
        """Validate that priorities sum to 1."""
        priorities = [v for k, v in values.items() if k.endswith("_priority")]
        priorities.append(v)
        if sum(priorities) != 1:
            raise ValueError("Priority values must sum to 1")
        return v 