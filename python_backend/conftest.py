import pytest
from typing import AsyncGenerator, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from mongomock_motor import AsyncMongoMockClient
from fastapi.testclient import TestClient
from main import app
from persistence.db_handler import db

@pytest.fixture
async def mock_db() -> AsyncGenerator[AsyncMongoMockClient, None]:
    """Create a mock MongoDB client."""
    client = AsyncMongoMockClient()
    db = client.test_db
    yield db
    await client.close()

@pytest.fixture
def test_client(mock_db: AsyncMongoMockClient) -> TestClient:
    """Create a test client with mocked database."""
    app.state.db = mock_db
    return TestClient(app)

@pytest.fixture
async def test_api_key(mock_db: AsyncMongoMockClient) -> str:
    """Create a test API key."""
    api_key = "test_api_key"
    await mock_db.api_keys.insert_one({
        "key": api_key,
        "client_id": "test_client",
        "is_active": True
    })
    return api_key

@pytest.fixture
def test_headers(test_api_key: str) -> Dict[str, str]:
    """Create test headers with API key."""
    return {"X-API-Key": test_api_key} 