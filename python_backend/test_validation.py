import pytest
from validation.validators import (
    validate_coordinates,
    validate_vehicle_data,
    validate_route_request,
    validate_api_key
)
from error_handling.exceptions import ValidationError

def test_coordinate_validation():
    """Test coordinate validation."""
    # Valid coordinates
    valid_coords = {"lat": 40.7128, "lon": -74.0060}
    assert validate_coordinates(valid_coords) is True
    
    # Invalid latitude
    with pytest.raises(ValidationError) as exc_info:
        validate_coordinates({"lat": 91.0, "lon": -74.0060})
    assert "latitude" in str(exc_info.value).lower()
    
    # Invalid longitude
    with pytest.raises(ValidationError) as exc_info:
        validate_coordinates({"lat": 40.7128, "lon": -181.0})
    assert "longitude" in str(exc_info.value).lower()

def test_vehicle_data_validation():
    """Test vehicle data validation."""
    # Valid vehicle data
    valid_vehicle = {
        "type": "light_duty",
        "fuel_type": "gasoline",
        "make": "Toyota",
        "model": "Corolla",
        "year": 2020,
        "cargo_capacity": 500.0,
        "fuel_efficiency": 12.5
    }
    assert validate_vehicle_data(valid_vehicle) is True
    
    # Invalid vehicle type
    with pytest.raises(ValidationError) as exc_info:
        invalid_vehicle = valid_vehicle.copy()
        invalid_vehicle["type"] = "invalid_type"
        validate_vehicle_data(invalid_vehicle)
    assert "vehicle type" in str(exc_info.value).lower()

def test_route_request_validation():
    """Test route request validation."""
    # Valid route request
    valid_request = {
        "start_point": {"lat": 40.7128, "lon": -74.0060},
        "end_point": {"lat": 40.7614, "lon": -73.9776},
        "vehicle_id": "test_vehicle_1",
        "preferences": ["eco_friendly"]
    }
    assert validate_route_request(valid_request) is True
    
    # Invalid preferences
    with pytest.raises(ValidationError) as exc_info:
        invalid_request = valid_request.copy()
        invalid_request["preferences"] = ["invalid_pref"]
        validate_route_request(invalid_request)
    assert "preferences" in str(exc_info.value).lower()

def test_api_key_validation():
    """Test API key validation."""
    # Valid API key
    valid_key = "test_key_12345"
    assert validate_api_key(valid_key) is True
    
    # Invalid API key format
    with pytest.raises(ValidationError) as exc_info:
        validate_api_key("invalid#key")
    assert "api key" in str(exc_info.value).lower() 