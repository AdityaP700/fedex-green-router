from typing import Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from persistence.db_handler import db

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verify API key and return client ID."""
    client = await db.api_keys.find_one({"key": api_key})
    if not client:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    return client["client_id"]

async def create_api_key(client_id: str, expires_in_days: Optional[int] = None) -> str:
    """Create a new API key for a client."""
    from secrets import token_urlsafe
    
    api_key = token_urlsafe(32)
    expires_at = None
    
    if expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    
    await db.api_keys.insert_one({
        "key": api_key,
        "client_id": client_id,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
        "is_active": True
    })
    
    return api_key

async def revoke_api_key(api_key: str) -> None:
    """Revoke an API key."""
    result = await db.api_keys.update_one(
        {"key": api_key},
        {"$set": {"is_active": False, "revoked_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail="API key not found"
        )
