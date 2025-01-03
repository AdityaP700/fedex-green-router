import pytest
from datetime import datetime, timedelta
from security.models import APIKey, Client
from security.auth import verify_api_key, create_api_key, revoke_api_key

async def test_api_key_model():
    """Test API key model."""
    api_key = APIKey(
        key="test_key",
        client_id="test_client",
        is_active=True
    )
    
    assert api_key.key == "test_key"
    assert api_key.client_id == "test_client"
    assert api_key.is_active is True
    assert isinstance(api_key.created_at, datetime)

async def test_client_model():
    """Test client model."""
    client = Client(
        client_id="test_client",
        name="Test Client",
        email="test@example.com"
    )
    
    assert client.client_id == "test_client"
    assert client.name == "Test Client"
    assert client.email == "test@example.com"
    assert client.rate_limit == 100

async def test_api_key_verification(mock_db, test_api_key):
    """Test API key verification."""
    # Test valid API key
    client_id = await verify_api_key(test_api_key)
    assert client_id == "test_client"
    
    # Test invalid API key
    with pytest.raises(Exception):
        await verify_api_key("invalid_key")

async def test_api_key_creation(mock_db):
    """Test API key creation."""
    api_key = await create_api_key(
        client_id="new_client",
        expires_in_days=30
    )
    
    assert api_key is not None
    
    # Verify in database
    key_doc = await mock_db.api_keys.find_one({"key": api_key})
    assert key_doc is not None
    assert key_doc["client_id"] == "new_client"
    assert key_doc["is_active"] is True

async def test_api_key_revocation(mock_db, test_api_key):
    """Test API key revocation."""
    await revoke_api_key(test_api_key)
    
    # Verify in database
    key_doc = await mock_db.api_keys.find_one({"key": test_api_key})
    assert key_doc is not None
    assert key_doc["is_active"] is False
    assert key_doc["revoked_at"] is not None 