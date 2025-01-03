from datetime import datetime
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase

async def upgrade(db: AsyncIOMotorDatabase):
    """Apply the migration."""
    # Create collections with schema validation
    await create_vehicles_collection(db)
    await create_routes_collection(db)
    await create_user_preferences_collection(db)
    await create_feedback_collection(db)
    await create_metrics_collection(db)
    await create_ml_models_collection(db)
    await create_maintenance_collection(db)

async def downgrade(db: AsyncIOMotorDatabase):
    """Revert the migration."""
    collections = [
        "vehicles", "routes", "user_preferences", "route_feedback",
        "performance_metrics", "ml_models", "maintenance_records"
    ]
    for collection in collections:
        await db.drop_collection(collection)

async def create_vehicles_collection(db: AsyncIOMotorDatabase):
    """Create vehicles collection with schema validation."""
    await db.create_collection(
        "vehicles",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "type", "fuel_type", "make", "model", "year", "cargo_capacity"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "type": {"enum": ["light_duty", "medium_duty", "heavy_duty", "electric", "hybrid"]},
                    "fuel_type": {"enum": ["gasoline", "diesel", "electric", "hybrid", "cng", "lng"]},
                    "make": {"bsonType": "string"},
                    "model": {"bsonType": "string"},
                    "year": {"bsonType": "int"},
                    "cargo_capacity": {"bsonType": "double"},
                    "current_load": {"bsonType": ["double", "null"]},
                    "fuel_efficiency": {"bsonType": "double"},
                    "maintenance_status": {"bsonType": ["string", "null"]},
                    "last_service_date": {"bsonType": ["date", "null"]}
                }
            }
        }
    )

async def create_routes_collection(db: AsyncIOMotorDatabase):
    """Create routes collection with schema validation."""
    await db.create_collection(
        "routes",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["start_point", "end_point", "total_distance", "total_duration"],
                "properties": {
                    "start_point": {
                        "bsonType": "object",
                        "required": ["lat", "lon"],
                        "properties": {
                            "lat": {"bsonType": "double"},
                            "lon": {"bsonType": "double"},
                            "address": {"bsonType": ["string", "null"]},
                            "name": {"bsonType": ["string", "null"]}
                        }
                    },
                    "end_point": {
                        "bsonType": "object",
                        "required": ["lat", "lon"],
                        "properties": {
                            "lat": {"bsonType": "double"},
                            "lon": {"bsonType": "double"},
                            "address": {"bsonType": ["string", "null"]},
                            "name": {"bsonType": ["string", "null"]}
                        }
                    },
                    "waypoints": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["lat", "lon"],
                            "properties": {
                                "lat": {"bsonType": "double"},
                                "lon": {"bsonType": "double"}
                            }
                        }
                    },
                    "total_distance": {"bsonType": "double"},
                    "total_duration": {"bsonType": "double"},
                    "total_emissions": {"bsonType": ["double", "null"]},
                    "traffic_delay": {"bsonType": ["double", "null"]},
                    "weather_conditions": {"bsonType": ["object", "null"]},
                    "air_quality": {"bsonType": ["object", "null"]}
                }
            }
        }
    )

async def create_user_preferences_collection(db: AsyncIOMotorDatabase):
    """Create user preferences collection with schema validation."""
    await db.create_collection(
        "user_preferences",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user_id"],
                "properties": {
                    "user_id": {"bsonType": "string"},
                    "route_preferences": {
                        "bsonType": "array",
                        "items": {
                            "enum": [
                                "eco_friendly", "speed", "cost_effective",
                                "ev_friendly", "avoid_tolls", "avoid_highways",
                                "scenic_route"
                            ]
                        }
                    },
                    "weather_preference": {
                        "enum": [
                            "avoid_snow", "avoid_rain",
                            "avoid_extreme_weather", "any_weather"
                        ]
                    },
                    "time_preference": {
                        "enum": [
                            "avoid_peak_hours", "flexible_timing",
                            "strict_timing"
                        ]
                    },
                    "max_route_options": {"bsonType": "int"},
                    "eco_score_threshold": {"bsonType": ["double", "null"]},
                    "max_emissions_threshold": {"bsonType": ["double", "null"]}
                }
            }
        }
    )

async def create_feedback_collection(db: AsyncIOMotorDatabase):
    """Create feedback collection with schema validation."""
    await db.create_collection(
        "route_feedback",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["route_id", "user_id", "vehicle_id", "rating", "timestamp"],
                "properties": {
                    "route_id": {"bsonType": "string"},
                    "user_id": {"bsonType": "string"},
                    "vehicle_id": {"bsonType": "string"},
                    "rating": {"bsonType": "int", "minimum": 1, "maximum": 5},
                    "actual_duration": {"bsonType": ["double", "null"]},
                    "actual_emissions": {"bsonType": ["double", "null"]},
                    "traffic_accuracy": {"bsonType": ["int", "null"]},
                    "weather_impact": {"bsonType": ["int", "null"]},
                    "comments": {"bsonType": ["string", "null"]},
                    "timestamp": {"bsonType": "date"}
                }
            }
        }
    )

async def create_metrics_collection(db: AsyncIOMotorDatabase):
    """Create metrics collection with schema validation."""
    await db.create_collection(
        "performance_metrics",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["timestamp", "metric_type", "value"],
                "properties": {
                    "timestamp": {"bsonType": "date"},
                    "metric_type": {"bsonType": "string"},
                    "value": {"bsonType": "double"},
                    "tags": {"bsonType": "object"}
                }
            }
        }
    )

async def create_ml_models_collection(db: AsyncIOMotorDatabase):
    """Create ML models collection with schema validation."""
    await db.create_collection(
        "ml_models",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["model_type", "version", "created_at", "metrics"],
                "properties": {
                    "model_type": {"enum": ["traffic", "emissions", "duration"]},
                    "version": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"},
                    "metrics": {
                        "bsonType": "object",
                        "required": ["accuracy", "mae", "rmse"],
                        "properties": {
                            "accuracy": {"bsonType": "double"},
                            "mae": {"bsonType": "double"},
                            "rmse": {"bsonType": "double"}
                        }
                    },
                    "hyperparameters": {"bsonType": "object"},
                    "feature_importance": {"bsonType": "object"}
                }
            }
        }
    )

async def create_maintenance_collection(db: AsyncIOMotorDatabase):
    """Create maintenance records collection with schema validation."""
    await db.create_collection(
        "maintenance_records",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["vehicle_id", "timestamp", "type"],
                "properties": {
                    "vehicle_id": {"bsonType": "string"},
                    "timestamp": {"bsonType": "date"},
                    "type": {"enum": ["routine", "repair", "inspection"]},
                    "description": {"bsonType": "string"},
                    "cost": {"bsonType": ["double", "null"]},
                    "technician": {"bsonType": ["string", "null"]},
                    "parts_replaced": {
                        "bsonType": ["array"],
                        "items": {"bsonType": "string"}
                    },
                    "next_service_date": {"bsonType": ["date", "null"]}
                }
            }
        }
    ) 