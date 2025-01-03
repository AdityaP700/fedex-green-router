from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class APIKey(BaseModel):
    """Model for API keys."""
    key: str = Field(..., description="API key")
    client_id: str = Field(..., description="Client identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    revoked_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Client(BaseModel):
    """Model for API clients."""
    client_id: str = Field(..., description="Client identifier")
    name: str = Field(..., description="Client name")
    email: str = Field(..., description="Client email")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    rate_limit: int = Field(default=100, description="Requests per minute")
    metadata: Dict[str, Any] = Field(default_factory=dict) 