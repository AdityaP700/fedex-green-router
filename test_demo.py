import asyncio
import httpx
from datetime import datetime, timedelta

async def test_api():
    """Test the core API functionalities."""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Create API key
        response = await client.post("/api/keys/create", json={
            "client_id": "test_client",
            "expires_in_days": 30
        })
        assert response.status_code == 200
        api_key = response.json()["api_key"]
        print(f"Created API key: {api_key}")
        
        # Set headers with API key
        headers = {"X-API-Key": api_key}
        
        # Create a vehicle
        response = await client.post("/vehicles/create", headers=headers, json={
            "id": "test_vehicle",
            "type": "electric",
            "cargo_capacity": 1000,
            "current_load": 500
        })
        assert response.status_code == 200
        vehicle = response.json()
        print(f"Created vehicle: {vehicle}")
        
        # Optimize a route
        departure_time = datetime.utcnow() + timedelta(hours=1)
        response = await client.post("/routes/optimize", headers=headers, json={
            "start_location": {"lat": 40.7128, "lon": -74.0060},  # New York
            "end_location": {"lat": 34.0522, "lon": -118.2437},   # Los Angeles
            "vehicle_id": "test_vehicle",
            "load_weight": 500,
            "departure_time": departure_time.isoformat()
        })
        assert response.status_code == 200
        route = response.json()
        print(f"Optimized route: {route}")
        
        # Get metrics
        response = await client.get("/metrics", headers=headers)
        assert response.status_code == 200
        metrics = response.json()
        print(f"Metrics: {metrics}")

if __name__ == "__main__":
    asyncio.run(test_api()) 