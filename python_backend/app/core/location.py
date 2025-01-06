from pydantic import BaseModel, Field

class Location(BaseModel):
    """Model representing a location with latitude and longitude."""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")

    def __str__(self) -> str:
        return f"({self.lat}, {self.lon})" 