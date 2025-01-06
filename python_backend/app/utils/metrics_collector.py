from typing import Dict, Any
from datetime import datetime
import uuid
from persistence.db_handler import db

class MetricsCollector:
    """Collects and stores application metrics."""
    
    async def start_request(self, endpoint: str) -> str:
        """Start tracking a request."""
        request_id = str(uuid.uuid4())
        
        await db.metrics.insert_one({
            "request_id": request_id,
            "endpoint": endpoint,
            "start_time": datetime.utcnow(),
            "status": "in_progress"
        })
        
        return request_id
    
    async def end_request(self, request_id: str, data: Dict[str, Any]):
        """End request tracking and store metrics."""
        end_time = datetime.utcnow()
        
        # Get start time
        request = await db.metrics.find_one({"request_id": request_id})
        if not request:
            return
            
        duration = (end_time - request["start_time"]).total_seconds()
        
        # Update metrics
        await db.metrics.update_one(
            {"request_id": request_id},
            {
                "$set": {
                    "end_time": end_time,
                    "duration": duration,
                    "status": "completed",
                    **data
                }
            }
        ) 