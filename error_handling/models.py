from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ErrorLog(BaseModel):
    """Model for error logging."""
    error_id: str = Field(..., description="Unique error identifier")
    error_type: str = Field(..., description="Type of error")
    message: str = Field(..., description="Error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    stack_trace: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict) 