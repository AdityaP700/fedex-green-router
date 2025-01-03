import pytest
from datetime import datetime
from error_handling.models import ErrorLog
from error_handling.exceptions import ValidationError, AuthenticationError, ResourceNotFoundError

async def test_error_log_creation():
    """Test creating an error log."""
    error_log = ErrorLog(
        error_id="test_error_1",
        error_type="validation_error",
        message="Invalid input data",
        stack_trace="...",
        request_data={"input": "invalid_data"}
    )
    
    assert error_log.error_id == "test_error_1"
    assert error_log.error_type == "validation_error"
    assert isinstance(error_log.timestamp, datetime)

def test_validation_error():
    """Test validation error."""
    with pytest.raises(ValidationError) as exc_info:
        raise ValidationError("Invalid input")
    assert str(exc_info.value) == "Invalid input"

def test_authentication_error():
    """Test authentication error."""
    with pytest.raises(AuthenticationError) as exc_info:
        raise AuthenticationError("Invalid API key")
    assert str(exc_info.value) == "Invalid API key"

def test_resource_not_found_error():
    """Test resource not found error."""
    with pytest.raises(ResourceNotFoundError) as exc_info:
        raise ResourceNotFoundError("Route not found")
    assert str(exc_info.value) == "Route not found" 