import pytest
from fastapi import status
from route_engine.route_optimizer import RouteOptimizer
from models.route import Route, RoutePoint
from models.vehicle import Vehicle

async def test_route_optimization_endpoint(test_app, test_data, mock_db, mock_redis):
    """Test the route optimization endpoint."""
    # Test data
    request_data = {
        "vehicle_id": "test_vehicle_1",
        "start_point": {"lat": 40.7128, "lon": -74.0060},
        "end_point": {"lat": 40.7614, "lon": -73.9776},
        "user_id": "test_user_1"
    }
    
    # Make request
    response = await test_app.post("/api/v1/routes/optimize", json=request_data)
    
    # Assertions
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "route_id" in data
    assert "total_distance" in data
    assert "total_duration" in data
    assert "total_emissions" in data
    assert "segments" in data
    assert len(data["segments"]) > 0

async def test_route_optimizer_calculation(mock_db, mock_redis, test_data):
    """Test the route optimization calculation logic."""
    # Initialize optimizer
    optimizer = RouteOptimizer()
    
    # Test data
    vehicle = Vehicle(**test_data["vehicles"][0])
    start_point = RoutePoint(lat=40.7128, lon=-74.0060)
    end_point = RoutePoint(lat=40.7614, lon=-73.9776)
    
    # Calculate route
    route = await optimizer.get_optimal_route(
        vehicle=vehicle,
        start_point=start_point,
        end_point=end_point,
        user_id="test_user_1"
    )
    
    # Assertions
    assert isinstance(route, Route)
    assert route.total_distance > 0
    assert route.total_duration > 0
    assert route.total_emissions >= 0
    assert len(route.segments) > 0

async def test_route_optimization_with_traffic(mock_db, mock_redis, test_data):
    """Test route optimization with traffic data."""
    optimizer = RouteOptimizer()
    
    # Mock traffic data in Redis
    traffic_key = "traffic:40.7128,-74.0060:40.7614,-73.9776"
    traffic_data = {
        "current_speed": 35,
        "free_flow_speed": 45,
        "congestion_level": "medium"
    }
    await mock_redis.set(traffic_key, str(traffic_data))
    
    # Calculate route
    vehicle = Vehicle(**test_data["vehicles"][0])
    start_point = RoutePoint(lat=40.7128, lon=-74.0060)
    end_point = RoutePoint(lat=40.7614, lon=-73.9776)
    
    route = await optimizer.get_optimal_route(
        vehicle=vehicle,
        start_point=start_point,
        end_point=end_point,
        user_id="test_user_1"
    )
    
    # Assertions
    assert route.traffic_level == "medium"
    assert route.total_duration > route.total_distance / 45  # Duration should be affected by traffic

async def test_route_optimization_with_weather(mock_db, mock_redis, test_data):
    """Test route optimization with weather data."""
    optimizer = RouteOptimizer()
    
    # Mock weather data in Redis
    weather_key = "weather:40.7128,-74.0060"
    weather_data = {
        "temperature": 20,
        "precipitation": 0.5,
        "wind_speed": 15,
        "condition": "rain"
    }
    await mock_redis.set(weather_key, str(weather_data))
    
    # Calculate route
    vehicle = Vehicle(**test_data["vehicles"][0])
    start_point = RoutePoint(lat=40.7128, lon=-74.0060)
    end_point = RoutePoint(lat=40.7614, lon=-73.9776)
    
    route = await optimizer.get_optimal_route(
        vehicle=vehicle,
        start_point=start_point,
        end_point=end_point,
        user_id="test_user_1"
    )
    
    # Assertions
    assert route.weather_condition == "rain"
    assert route.total_emissions > route.total_distance * vehicle.fuel_efficiency  # Emissions should be affected by weather

async def test_route_optimization_with_preferences(mock_db, mock_redis, test_data):
    """Test route optimization with user preferences."""
    optimizer = RouteOptimizer()
    
    # Calculate route for eco-friendly user
    vehicle = Vehicle(**test_data["vehicles"][0])
    start_point = RoutePoint(lat=40.7128, lon=-74.0060)
    end_point = RoutePoint(lat=40.7614, lon=-73.9776)
    
    eco_route = await optimizer.get_optimal_route(
        vehicle=vehicle,
        start_point=start_point,
        end_point=end_point,
        user_id="test_user_1"  # User with eco_friendly preference
    )
    
    speed_route = await optimizer.get_optimal_route(
        vehicle=vehicle,
        start_point=start_point,
        end_point=end_point,
        user_id="test_user_2"  # User with speed preference
    )
    
    # Assertions
    assert eco_route.total_emissions < speed_route.total_emissions
    assert eco_route.total_duration > speed_route.total_duration

async def test_route_optimization_error_handling(test_app):
    """Test error handling in route optimization."""
    # Test invalid coordinates
    invalid_request = {
        "vehicle_id": "test_vehicle_1",
        "start_point": {"lat": 91, "lon": -74.0060},  # Invalid latitude
        "end_point": {"lat": 40.7614, "lon": -73.9776},
        "user_id": "test_user_1"
    }
    
    response = await test_app.post("/api/v1/routes/optimize", json=invalid_request)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Test missing vehicle
    missing_vehicle_request = {
        "vehicle_id": "non_existent_vehicle",
        "start_point": {"lat": 40.7128, "lon": -74.0060},
        "end_point": {"lat": 40.7614, "lon": -73.9776},
        "user_id": "test_user_1"
    }
    
    response = await test_app.post("/api/v1/routes/optimize", json=missing_vehicle_request)
    assert response.status_code == status.HTTP_404_NOT_FOUND 