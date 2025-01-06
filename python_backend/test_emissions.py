import pytest
from emissions.emissions_calculator import EmissionsCalculator
from models.vehicle import Vehicle
from models.route import Route, RoutePoint, RouteSegment

async def test_base_emissions_calculation(test_data):
    """Test the base emissions calculation without external factors."""
    calculator = EmissionsCalculator()
    
    # Test data
    vehicle = Vehicle(**test_data["vehicles"][0])  # Gasoline vehicle
    route = Route(
        id="test_route",
        start_point=RoutePoint(lat=40.7128, lon=-74.0060),
        end_point=RoutePoint(lat=40.7614, lon=-73.9776),
        total_distance=5.2,
        total_duration=15.5,
        segments=[
            RouteSegment(
                start_point=RoutePoint(lat=40.7128, lon=-74.0060),
                end_point=RoutePoint(lat=40.7614, lon=-73.9776),
                distance=5.2,
                duration=15.5
            )
        ]
    )
    
    # Calculate emissions
    emissions = await calculator._calculate_base_emissions(vehicle, route)
    
    # Assertions
    assert emissions > 0
    assert emissions == pytest.approx(route.total_distance * vehicle.fuel_efficiency, rel=0.1)

async def test_weather_impact_on_emissions(test_data, mock_redis):
    """Test the impact of weather conditions on emissions calculations."""
    calculator = EmissionsCalculator()
    
    # Mock weather data
    weather_data = {
        "temperature": 20,
        "precipitation": 0.5,
        "wind_speed": 15,
        "condition": "rain"
    }
    await mock_redis.set("weather:40.7128,-74.0060", str(weather_data))
    
    # Test data
    vehicle = Vehicle(**test_data["vehicles"][0])
    route = Route(
        id="test_route",
        start_point=RoutePoint(lat=40.7128, lon=-74.0060),
        end_point=RoutePoint(lat=40.7614, lon=-73.9776),
        total_distance=5.2,
        total_duration=15.5,
        segments=[
            RouteSegment(
                start_point=RoutePoint(lat=40.7128, lon=-74.0060),
                end_point=RoutePoint(lat=40.7614, lon=-73.9776),
                distance=5.2,
                duration=15.5
            )
        ]
    )
    
    # Calculate weather impact
    weather_factor = await calculator._calculate_weather_impact(route.start_point)
    
    # Assertions
    assert weather_factor > 1.0  # Bad weather should increase emissions
    assert weather_factor == pytest.approx(1.2, rel=0.2)  # Approximate impact for rain

async def test_traffic_impact_on_emissions(test_data, mock_redis):
    """Test the impact of traffic conditions on emissions calculations."""
    calculator = EmissionsCalculator()
    
    # Mock traffic data
    traffic_data = {
        "current_speed": 35,
        "free_flow_speed": 45,
        "congestion_level": "medium"
    }
    await mock_redis.set("traffic:40.7128,-74.0060:40.7614,-73.9776", str(traffic_data))
    
    # Test data
    vehicle = Vehicle(**test_data["vehicles"][0])
    route = Route(
        id="test_route",
        start_point=RoutePoint(lat=40.7128, lon=-74.0060),
        end_point=RoutePoint(lat=40.7614, lon=-73.9776),
        total_distance=5.2,
        total_duration=15.5,
        segments=[
            RouteSegment(
                start_point=RoutePoint(lat=40.7128, lon=-74.0060),
                end_point=RoutePoint(lat=40.7614, lon=-73.9776),
                distance=5.2,
                duration=15.5
            )
        ]
    )
    
    # Calculate traffic impact
    traffic_factor = await calculator._calculate_traffic_impact(route.start_point, route.end_point)
    
    # Assertions
    assert traffic_factor > 1.0  # Congestion should increase emissions
    assert traffic_factor == pytest.approx(1.15, rel=0.2)  # Approximate impact for medium congestion

async def test_electric_vehicle_emissions(test_data):
    """Test emissions calculations for electric vehicles."""
    calculator = EmissionsCalculator()
    
    # Test data
    vehicle = Vehicle(**test_data["vehicles"][1])  # Electric vehicle
    route = Route(
        id="test_route",
        start_point=RoutePoint(lat=40.7128, lon=-74.0060),
        end_point=RoutePoint(lat=40.7614, lon=-73.9776),
        total_distance=5.2,
        total_duration=15.5,
        segments=[
            RouteSegment(
                start_point=RoutePoint(lat=40.7128, lon=-74.0060),
                end_point=RoutePoint(lat=40.7614, lon=-73.9776),
                distance=5.2,
                duration=15.5
            )
        ]
    )
    
    # Calculate emissions
    emissions = await calculator._calculate_base_emissions(vehicle, route)
    
    # Assertions
    assert emissions >= 0
    assert emissions < (route.total_distance * 0.5)  # Electric vehicles should have significantly lower emissions

async def test_emission_reduction_suggestions(test_data):
    """Test generation of emission reduction suggestions."""
    calculator = EmissionsCalculator()
    
    # Test data
    vehicle = Vehicle(**test_data["vehicles"][0])
    route = Route(
        id="test_route",
        start_point=RoutePoint(lat=40.7128, lon=-74.0060),
        end_point=RoutePoint(lat=40.7614, lon=-73.9776),
        total_distance=5.2,
        total_duration=15.5,
        segments=[
            RouteSegment(
                start_point=RoutePoint(lat=40.7128, lon=-74.0060),
                end_point=RoutePoint(lat=40.7614, lon=-73.9776),
                distance=5.2,
                duration=15.5
            )
        ]
    )
    
    # Get suggestions
    suggestions = await calculator.get_emission_reduction_suggestions(vehicle, route)
    
    # Assertions
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0
    assert all(isinstance(suggestion, str) for suggestion in suggestions)

async def test_emissions_api_endpoint(test_app, test_data):
    """Test the emissions calculation API endpoint."""
    # Test data
    request_data = {
        "route_id": "test_route_1",
        "vehicle_id": "test_vehicle_1"
    }
    
    # Make request
    response = await test_app.post("/api/v1/emissions/calculate", json=request_data)
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "total_emissions" in data
    assert "reduction_suggestions" in data
    assert isinstance(data["reduction_suggestions"], list) 