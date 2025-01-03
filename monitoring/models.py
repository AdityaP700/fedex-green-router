from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class RequestMetrics(BaseModel):
    """Model for request metrics."""
    request_id: str = Field(..., description="Unique request identifier")
    endpoint: str = Field(..., description="API endpoint")
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    status: str = Field(..., description="Request status")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PerformanceMetrics(BaseModel):
    """Model for performance metrics."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    active_connections: int = Field(..., description="Number of active connections")
    response_times: Dict[str, float] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict) 