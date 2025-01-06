import pytest
from datetime import datetime, timedelta
from monitoring.models import RequestMetrics, PerformanceMetrics
from monitoring.metrics_collector import MetricsCollector

async def test_request_metrics_creation():
    """Test creating request metrics."""
    metrics = RequestMetrics(
        request_id="test_request_1",
        endpoint="/api/routes/optimize",
        status="success"
    )
    
    assert metrics.request_id == "test_request_1"
    assert metrics.endpoint == "/api/routes/optimize"
    assert isinstance(metrics.start_time, datetime)
    assert metrics.end_time is None
    assert metrics.duration is None

async def test_performance_metrics_creation():
    """Test creating performance metrics."""
    metrics = PerformanceMetrics(
        cpu_usage=45.5,
        memory_usage=60.2,
        active_connections=10,
        response_times={
            "/api/routes/optimize": 0.5,
            "/api/vehicles": 0.2
        }
    )
    
    assert metrics.cpu_usage == 45.5
    assert metrics.memory_usage == 60.2
    assert metrics.active_connections == 10
    assert len(metrics.response_times) == 2

async def test_metrics_collector(mock_db):
    """Test metrics collector functionality."""
    collector = MetricsCollector()
    
    # Start request tracking
    request_id = await collector.start_request("test_endpoint")
    assert request_id is not None
    
    # End request tracking
    await collector.end_request(request_id, {
        "status": "success",
        "duration": 0.5
    })
    
    # Verify metrics in database
    metrics = await mock_db.metrics.find_one({"request_id": request_id})
    assert metrics is not None
    assert metrics["status"] == "success"
    assert metrics["duration"] == 0.5 