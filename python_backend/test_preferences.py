import pytest
from fastapi import status
from preferences.user_preferences import PreferenceHandler, RoutePreferenceType, WeatherPreference, TimePreference

async def test_preference_creation(test_app, test_data):
    """Test creating user preferences."""
    # Test data
    preference_data = {
        "user_id": "new_test_user",
        "route_preferences": ["eco_friendly"],
        "weather_preference": "any_weather",
        "time_preference": "flexible_timing",
        "max_route_options": 3
    }
    
    # Make request
    response = await test_app.post("/api/v1/preferences", json=preference_data)
    
    # Assertions
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user_id"] == preference_data["user_id"]
    assert data["route_preferences"] == preference_data["route_preferences"]
    assert data["weather_preference"] == preference_data["weather_preference"]
    assert data["time_preference"] == preference_data["time_preference"]
    assert data["max_route_options"] == preference_data["max_route_options"]

async def test_preference_retrieval(test_app, test_data):
    """Test retrieving user preferences."""
    # Make request
    response = await test_app.get("/api/v1/preferences/test_user_1")
    
    # Assertions
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["user_id"] == "test_user_1"
    assert "eco_friendly" in data["route_preferences"]
    assert data["weather_preference"] == "any_weather"
    assert data["time_preference"] == "flexible_timing"
    assert data["max_route_options"] == 3

async def test_preference_update(test_app, test_data):
    """Test updating user preferences."""
    # Test data
    update_data = {
        "route_preferences": ["speed", "eco_friendly"],
        "weather_preference": "avoid_rain",
        "time_preference": "strict_timing"
    }
    
    # Make request
    response = await test_app.patch("/api/v1/preferences/test_user_1", json=update_data)
    
    # Assertions
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["user_id"] == "test_user_1"
    assert set(data["route_preferences"]) == set(update_data["route_preferences"])
    assert data["weather_preference"] == update_data["weather_preference"]
    assert data["time_preference"] == update_data["time_preference"]

async def test_preference_deletion(test_app, test_data):
    """Test deleting user preferences."""
    # Make request
    response = await test_app.delete("/api/v1/preferences/test_user_1")
    
    # Assertions
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify deletion
    get_response = await test_app.get("/api/v1/preferences/test_user_1")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

async def test_preference_validation(test_app):
    """Test preference validation."""
    # Test invalid route preference
    invalid_preference_data = {
        "user_id": "test_user",
        "route_preferences": ["invalid_preference"],
        "weather_preference": "any_weather",
        "time_preference": "flexible_timing",
        "max_route_options": 3
    }
    
    response = await test_app.post("/api/v1/preferences", json=invalid_preference_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Test invalid weather preference
    invalid_weather_data = {
        "user_id": "test_user",
        "route_preferences": ["eco_friendly"],
        "weather_preference": "invalid_weather",
        "time_preference": "flexible_timing",
        "max_route_options": 3
    }
    
    response = await test_app.post("/api/v1/preferences", json=invalid_weather_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Test invalid time preference
    invalid_time_data = {
        "user_id": "test_user",
        "route_preferences": ["eco_friendly"],
        "weather_preference": "any_weather",
        "time_preference": "invalid_time",
        "max_route_options": 3
    }
    
    response = await test_app.post("/api/v1/preferences", json=invalid_time_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

async def test_preference_handler(test_data):
    """Test the PreferenceHandler class."""
    handler = PreferenceHandler()
    
    # Test getting routing factors for eco-friendly preference
    eco_factors = await handler.get_routing_factors(
        user_id="test_user_1",  # User with eco_friendly preference
        current_weather="clear",
        current_traffic="low"
    )
    
    assert eco_factors.emissions_weight > eco_factors.speed_weight
    assert eco_factors.weather_weight > 0
    assert eco_factors.traffic_weight > 0
    
    # Test getting routing factors for speed preference
    speed_factors = await handler.get_routing_factors(
        user_id="test_user_2",  # User with speed preference
        current_weather="clear",
        current_traffic="low"
    )
    
    assert speed_factors.speed_weight > speed_factors.emissions_weight
    assert speed_factors.weather_weight > 0
    assert speed_factors.traffic_weight > 0

async def test_preference_merging(test_data):
    """Test merging multiple preferences."""
    handler = PreferenceHandler()
    
    # Test merging eco-friendly and speed preferences
    merged_factors = await handler.merge_preferences(
        preferences=[RoutePreferenceType.ECO_FRIENDLY, RoutePreferenceType.SPEED],
        weather_preference=WeatherPreference.ANY_WEATHER,
        time_preference=TimePreference.FLEXIBLE_TIMING
    )
    
    assert merged_factors.emissions_weight > 0
    assert merged_factors.speed_weight > 0
    assert merged_factors.emissions_weight == pytest.approx(merged_factors.speed_weight, rel=0.1)

async def test_default_preferences():
    """Test default preference handling."""
    handler = PreferenceHandler()
    
    # Test getting routing factors for non-existent user (should use defaults)
    default_factors = await handler.get_routing_factors(
        user_id="non_existent_user",
        current_weather="clear",
        current_traffic="low"
    )
    
    assert default_factors.emissions_weight > 0
    assert default_factors.speed_weight > 0
    assert default_factors.weather_weight > 0
    assert default_factors.traffic_weight > 0 