from fastapi import APIRouter, HTTPException
from typing import Dict
from .auth import create_api_key, revoke_api_key

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/api-key")
async def create_new_api_key(request: Dict[str, str]) -> Dict[str, str]:
    """Create a new API key for a client."""
    if "client_id" not in request:
        raise HTTPException(status_code=400, detail="client_id is required")
    
    api_key = await create_api_key(request["client_id"])
    return {"api_key": api_key}

@router.delete("/api-key/{api_key}")
async def revoke_existing_api_key(api_key: str) -> Dict[str, str]:
    """Revoke an existing API key."""
    await revoke_api_key(api_key)
    return {"message": "API key revoked successfully"} 