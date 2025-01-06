from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from datetime import datetime
from security.auth import verify_api_key
from monitoring.metrics_collector import MetricsCollector
from .route_optimizer import RouteOptimizer
from validation.validators import RouteValidator

router = APIRouter(prefix="/routes", tags=["routes"])
metrics_collector = MetricsCollector()
route_optimizer = RouteOptimizer()

@router.post("/optimize")
async def optimize_route(
    route_data: RouteValidator,
    client_id: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """Optimize a route based on given parameters."""
    try:
        request_id = await metrics_collector.start_request("optimize_route")
        
        optimized_route = await route_optimizer.optimize(
            start_location=route_data.start_location.dict(),
            end_location=route_data.end_location.dict(),
            waypoints=[wp.dict() for wp in route_data.waypoints] if route_data.waypoints else [],
            vehicle_id=route_data.vehicle_id,
            load_weight=route_data.load_weight,
            departure_time=route_data.departure_time
        )
        
        await metrics_collector.end_request(
            request_id,
            {
                "status": "success",
                "route_id": optimized_route["id"],
                "distance": optimized_route["total_distance"],
                "duration": optimized_route["total_duration"]
            }
        )
        
        return optimized_route
        
    except Exception as e:
        if 'request_id' in locals():
            await metrics_collector.end_request(
                request_id,
                {"status": "error", "error": str(e)}
            )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{route_id}")
async def get_route(
    route_id: str,
    client_id: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """Get details of a specific route."""
    try:
        request_id = await metrics_collector.start_request("get_route")
        
        route = await route_optimizer.get_route(route_id)
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        await metrics_collector.end_request(
            request_id,
            {"status": "success"}
        )
        
        return route
        
    except HTTPException:
        raise
    except Exception as e:
        if 'request_id' in locals():
            await metrics_collector.end_request(
                request_id,
                {"status": "error", "error": str(e)}
            )
        raise HTTPException(status_code=500, detail=str(e)) 