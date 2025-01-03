from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Dict, Any
from security.auth import verify_api_key
from monitoring.metrics_collector import MetricsCollector

router = APIRouter(prefix="/metrics", tags=["metrics"])
metrics_collector = MetricsCollector()

@router.get("/")
async def get_metrics(
    start_time: datetime,
    end_time: datetime,
    _: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """Get system metrics for a specific time period."""
    return await metrics_collector.get_metrics(start_time, end_time)

@router.get("/errors")
async def get_errors(
    start_time: datetime,
    end_time: datetime,
    _: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """Get error metrics for a specific time period."""
    pipeline = [
        {
            "$match": {
                "timestamp": {"$gte": start_time, "$lte": end_time}
            }
        },
        {
            "$group": {
                "_id": "$status_code",
                "count": {"$sum": 1},
                "errors": {
                    "$push": {
                        "message": "$error_message",
                        "timestamp": "$timestamp"
                    }
                }
            }
        }
    ]
    
    results = await metrics_collector.db.errors.aggregate(pipeline).to_list(None)
    return {
        "errors": results,
        "period": {
            "start": start_time,
            "end": end_time
        }
    } 