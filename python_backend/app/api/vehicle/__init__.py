from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(
    prefix="/api/vehicles",
    tags=["vehicles"],
    responses={404: {"description": "Not found"}},
)

class VehicleType(BaseModel):
    name: str
    category: str
    fuel_type: str
    fuel_efficiency: float  # km/L
    cargo_capacity: float   # kg
    emission_factor: float  # g CO2/km
    maintenance_status: str
    last_service_date: Optional[datetime] = None

# Predefined vehicle types with their characteristics
PREDEFINED_VEHICLES = {
    "sprinter_van": VehicleType(
        name="Sprinter Van",
        category="van",
        fuel_type="diesel",
        fuel_efficiency=12.0,
        cargo_capacity=2000,
        emission_factor=200,
        maintenance_status="good"
    ),
    "electric_van": VehicleType(
        name="Electric Van",
        category="van",
        fuel_type="electric",
        fuel_efficiency=0.0,  # kWh/km instead
        cargo_capacity=1800,
        emission_factor=0,    # Direct emissions
        maintenance_status="excellent"
    ),
    "box_truck": VehicleType(
        name="Box Truck",
        category="truck",
        fuel_type="diesel",
        fuel_efficiency=8.0,
        cargo_capacity=5000,
        emission_factor=300,
        maintenance_status="good"
    ),
    "cargo_bike": VehicleType(
        name="Cargo Bike",
        category="bike",
        fuel_type="human",
        fuel_efficiency=0.0,
        cargo_capacity=100,
        emission_factor=0,
        maintenance_status="excellent"
    )
}

@router.get("/types")
async def get_vehicle_types() -> Dict[str, VehicleType]:
    """Get all predefined vehicle types."""
    return PREDEFINED_VEHICLES

@router.get("/type/{vehicle_type}")
async def get_vehicle_type(vehicle_type: str) -> VehicleType:
    """Get details for a specific vehicle type."""
    if vehicle_type not in PREDEFINED_VEHICLES:
        raise HTTPException(status_code=404, detail="Vehicle type not found")
    return PREDEFINED_VEHICLES[vehicle_type]

class EmissionEstimate(BaseModel):
    vehicle_type: str
    distance: float  # km
    cargo_weight: float  # kg
    estimated_emissions: float  # g CO2
    fuel_consumption: float  # L or kWh
    route_efficiency_score: float  # 0-100

@router.post("/estimate-emissions")
async def estimate_emissions(
    vehicle_type: str,
    distance: float,
    cargo_weight: float,
    route_gradient: float = 0.0,  # Average route gradient in degrees
    temperature: float = 20.0,    # Ambient temperature in Celsius
) -> EmissionEstimate:
    """
    Estimate emissions for a given vehicle type and route parameters.
    Takes into account:
    - Vehicle characteristics
    - Distance
    - Cargo weight
    - Route gradient
    - Temperature (affects efficiency)
    """
    if vehicle_type not in PREDEFINED_VEHICLES:
        raise HTTPException(status_code=404, detail="Vehicle type not found")
    
    vehicle = PREDEFINED_VEHICLES[vehicle_type]
    
    # Basic emission calculation
    base_emissions = distance * vehicle.emission_factor
    
    # Weight factor (every 10% increase in weight increases emissions by 2%)
    weight_factor = 1 + (cargo_weight / vehicle.cargo_capacity) * 0.2
    
    # Temperature factor (extreme temperatures reduce efficiency)
    temp_factor = 1 + abs(temperature - 20) * 0.01
    
    # Gradient factor (each degree increases emissions by 3%)
    gradient_factor = 1 + abs(route_gradient) * 0.03
    
    # Calculate total emissions
    total_emissions = base_emissions * weight_factor * temp_factor * gradient_factor
    
    # Calculate fuel consumption
    fuel_consumption = (distance / vehicle.fuel_efficiency) if vehicle.fuel_efficiency > 0 else 0
    
    # Calculate route efficiency score (100 is best)
    efficiency_score = 100 - (
        (weight_factor - 1) * 30 +  # Weight penalty
        (temp_factor - 1) * 20 +    # Temperature penalty
        (gradient_factor - 1) * 50   # Gradient penalty
    )
    efficiency_score = max(0, min(100, efficiency_score))
    
    return EmissionEstimate(
        vehicle_type=vehicle_type,
        distance=distance,
        cargo_weight=cargo_weight,
        estimated_emissions=total_emissions,
        fuel_consumption=fuel_consumption,
        route_efficiency_score=efficiency_score
    )
