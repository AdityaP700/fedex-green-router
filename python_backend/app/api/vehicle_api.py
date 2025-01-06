from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from models.vehicle import Vehicle
from persistence.db_handler import db
from security.auth import verify_api_key
from monitoring.metrics_collector import MetricsCollector

router = APIRouter(prefix="/vehicles", tags=["vehicles"])
metrics_collector = MetricsCollector()

@router.post("/", response_model=Vehicle)
async def create_vehicle(vehicle: Vehicle):
    """Create a new vehicle in the system."""
    try:
        request_id = await metrics_collector.start_request("create_vehicle")
        vehicle_dict = vehicle.dict()
        result = await db.insert_one("vehicles", vehicle_dict)
        vehicle_dict["id"] = str(result.inserted_id)
        
        await metrics_collector.end_request(
            request_id,
            {"status": "success", "vehicle_id": vehicle_dict["id"]}
        )
        return vehicle_dict
    except Exception as e:
        if 'request_id' in locals():
            await metrics_collector.end_request(
                request_id,
                {"status": "error", "error": str(e)}
            )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(vehicle_id: str):
    """Get vehicle details by ID."""
    try:
        request_id = await metrics_collector.start_request("get_vehicle")
        vehicle = await db.find_one("vehicles", {"id": vehicle_id})
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        await metrics_collector.end_request(
            request_id,
            {"status": "success"}
        )
        return vehicle
    except Exception as e:
        if 'request_id' in locals():
            await metrics_collector.end_request(
                request_id,
                {"status": "error", "error": str(e)}
            )
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{vehicle_id}", response_model=Vehicle)
async def update_vehicle(vehicle_id: str, vehicle: Vehicle):
    """Update vehicle details."""
    try:
        request_id = await metrics_collector.start_request("update_vehicle")
        vehicle_dict = vehicle.dict()
        result = await db.update_one(
            "vehicles",
            {"id": vehicle_id},
            {"$set": vehicle_dict}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        await metrics_collector.end_request(
            request_id,
            {"status": "success"}
        )
        return vehicle_dict
    except Exception as e:
        if 'request_id' in locals():
            await metrics_collector.end_request(
                request_id,
                {"status": "error", "error": str(e)}
            )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Vehicle])
async def list_vehicles(
    type: Optional[str] = None,
    fuel_type: Optional[str] = None,
    available: Optional[bool] = None
):
    """List vehicles with optional filters."""
    try:
        request_id = await metrics_collector.start_request("list_vehicles")
        query = {}
        if type:
            query["type"] = type
        if fuel_type:
            query["fuel_type"] = fuel_type
        if available is not None:
            query["available"] = available
            
        vehicles = await db.find("vehicles", query)
        
        await metrics_collector.end_request(
            request_id,
            {"status": "success", "count": len(vehicles)}
        )
        return vehicles
    except Exception as e:
        if 'request_id' in locals():
            await metrics_collector.end_request(
                request_id,
                {"status": "error", "error": str(e)}
            )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{vehicle_id}/maintenance")
async def record_maintenance(
    vehicle_id: str,
    maintenance_data: dict
):
    """Record vehicle maintenance activity."""
    try:
        request_id = await metrics_collector.start_request("record_maintenance")
        vehicle = await db.find_one("vehicles", {"id": vehicle_id})
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
            
        maintenance_data["timestamp"] = datetime.now()
        maintenance_data["vehicle_id"] = vehicle_id
        
        await db.insert_one("maintenance_records", maintenance_data)
        await db.update_one(
            "vehicles",
            {"id": vehicle_id},
            {
                "$set": {
                    "last_service_date": maintenance_data["timestamp"],
                    "maintenance_status": maintenance_data.get("status", "serviced")
                }
            }
        )
        
        await metrics_collector.end_request(
            request_id,
            {"status": "success"}
        )
        return {"message": "Maintenance record added successfully"}
    except Exception as e:
        if 'request_id' in locals():
            await metrics_collector.end_request(
                request_id,
                {"status": "error", "error": str(e)}
            )
        raise HTTPException(status_code=500, detail=str(e)) 