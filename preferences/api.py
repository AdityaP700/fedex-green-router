from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from preferences.user_preferences import UserPreferences, PreferenceHandler
from persistence.db_handler import db
from security.auth import verify_api_key
from monitoring.metrics_collector import MetricsCollector

router = APIRouter(prefix="/preferences", tags=["preferences"])
metrics_collector = MetricsCollector()

@router.post("/users/{user_id}", response_model=UserPreferences)
async def set_user_preferences(
    user_id: str,
    preferences: UserPreferences
):
    """Set or update user preferences."""
    try:
        request_id = await metrics_collector.start_request("set_preferences")
        
        # Validate preferences
        if not PreferenceHandler.validate_preferences(preferences):
            raise HTTPException(
                status_code=400,
                detail="Invalid preference configuration"
            )
        
        # Check for existing preferences
        existing = await db.find_one(
            "user_preferences",
            {"user_id": user_id}
        )
        
        if existing:
            # Update existing preferences
            preferences_dict = preferences.dict()
            await db.update_one(
                "user_preferences",
                {"user_id": user_id},
                {"$set": preferences_dict}
            )
        else:
            # Create new preferences
            preferences_dict = preferences.dict()
            await db.insert_one("user_preferences", preferences_dict)
        
        await metrics_collector.end_request(
            request_id,
            {"status": "success"}
        )
        return preferences
    except Exception as e:
        if 'request_id' in locals():
            await metrics_collector.end_request(
                request_id,
                {"status": "error", "error": str(e)}
            )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}", response_model=UserPreferences)
async def get_user_preferences(user_id: str):
    """Get user preferences."""
    try:
        request_id = await metrics_collector.start_request("get_preferences")
        
        preferences = await db.find_one(
            "user_preferences",
            {"user_id": user_id}
        )
        
        if not preferences:
            raise HTTPException(
                status_code=404,
                detail="Preferences not found for user"
            )
        
        await metrics_collector.end_request(
            request_id,
            {"status": "success"}
        )
        return UserPreferences(**preferences)
    except Exception as e:
        if 'request_id' in locals():
            await metrics_collector.end_request(
                request_id,
                {"status": "error", "error": str(e)}
            )
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/users/{user_id}", response_model=UserPreferences)
async def update_user_preferences(
    user_id: str,
    preferences: UserPreferences
):
    """Partially update user preferences."""
    try:
        request_id = await metrics_collector.start_request("update_preferences")
        
        # Get existing preferences
        existing = await db.find_one(
            "user_preferences",
            {"user_id": user_id}
        )
        
        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Preferences not found for user"
            )
        
        # Merge preferences
        merged = PreferenceHandler.merge_preferences(
            UserPreferences(**existing),
            preferences
        )
        
        # Validate merged preferences
        if not PreferenceHandler.validate_preferences(merged):
            raise HTTPException(
                status_code=400,
                detail="Invalid preference configuration after merge"
            )
        
        # Update preferences
        merged_dict = merged.dict()
        await db.update_one(
            "user_preferences",
            {"user_id": user_id},
            {"$set": merged_dict}
        )
        
        await metrics_collector.end_request(
            request_id,
            {"status": "success"}
        )
        return merged
    except Exception as e:
        if 'request_id' in locals():
            await metrics_collector.end_request(
                request_id,
                {"status": "error", "error": str(e)}
            )
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
async def delete_user_preferences(user_id: str):
    """Delete user preferences."""
    try:
        request_id = await metrics_collector.start_request("delete_preferences")
        
        result = await db.delete_one(
            "user_preferences",
            {"user_id": user_id}
        )
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Preferences not found for user"
            )
        
        await metrics_collector.end_request(
            request_id,
            {"status": "success"}
        )
        return {"message": "Preferences deleted successfully"}
    except Exception as e:
        if 'request_id' in locals():
            await metrics_collector.end_request(
                request_id,
                {"status": "error", "error": str(e)}
            )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/defaults", response_model=UserPreferences)
async def get_default_preferences():
    """Get default user preferences."""
    try:
        request_id = await metrics_collector.start_request("get_default_preferences")
        
        defaults = UserPreferences(
            user_id="default",
            route_preferences=[],
            weather_preference="any_weather",
            time_preference="flexible_timing",
            max_route_options=3
        )
        
        await metrics_collector.end_request(
            request_id,
            {"status": "success"}
        )
        return defaults
    except Exception as e:
        if 'request_id' in locals():
            await metrics_collector.end_request(
                request_id,
                {"status": "error", "error": str(e)}
            )
        raise HTTPException(status_code=500, detail=str(e)) 