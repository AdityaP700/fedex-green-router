import pytest
from fastapi import status
from feedback.feedback_handler import FeedbackHandler, RouteFeedback, FeedbackAnalytics
from models.route import Route, RoutePoint, RouteSegment

async def test_feedback_submission(test_app, test_data):
    """Test submitting route feedback."""
    # Test data
    feedback_data = {
        "route_id": "test_route_1",
        "user_id": "test_user_1",
        "rating": 4,
        "accuracy": {
            "traffic_accuracy": 0.85,
            "weather_accuracy": 0.9,
            "emissions_accuracy": 0.8
        },
        "comments": "Route was efficient but traffic prediction was slightly off",
        "suggestions": ["Improve traffic prediction", "Add more alternative routes"]
    }
    
    # Make request
    response = await test_app.post("/api/v1/feedback", json=feedback_data)
    
    # Assertions
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["route_id"] == feedback_data["route_id"]
    assert data["user_id"] == feedback_data["user_id"]
    assert data["rating"] == feedback_data["rating"]
    assert data["accuracy"] == feedback_data["accuracy"]
    assert data["comments"] == feedback_data["comments"]
    assert data["suggestions"] == feedback_data["suggestions"]

async def test_feedback_retrieval(test_app, test_data):
    """Test retrieving feedback for a specific route."""
    # Make request
    response = await test_app.get("/api/v1/feedback/test_route_1")
    
    # Assertions
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(isinstance(feedback, dict) for feedback in data)
    assert all("route_id" in feedback for feedback in data)
    assert all("rating" in feedback for feedback in data)

async def test_feedback_analytics(test_app, test_data):
    """Test generating feedback analytics."""
    # Make request
    response = await test_app.get("/api/v1/feedback/analytics")
    
    # Assertions
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "average_rating" in data
    assert "accuracy_metrics" in data
    assert "common_suggestions" in data
    assert isinstance(data["average_rating"], float)
    assert isinstance(data["accuracy_metrics"], dict)
    assert isinstance(data["common_suggestions"], list)

async def test_feedback_validation(test_app):
    """Test feedback validation."""
    # Test invalid rating
    invalid_rating_data = {
        "route_id": "test_route_1",
        "user_id": "test_user_1",
        "rating": 6,  # Invalid rating (should be 1-5)
        "accuracy": {
            "traffic_accuracy": 0.85,
            "weather_accuracy": 0.9,
            "emissions_accuracy": 0.8
        }
    }
    
    response = await test_app.post("/api/v1/feedback", json=invalid_rating_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Test invalid accuracy values
    invalid_accuracy_data = {
        "route_id": "test_route_1",
        "user_id": "test_user_1",
        "rating": 4,
        "accuracy": {
            "traffic_accuracy": 1.2,  # Invalid accuracy (should be 0-1)
            "weather_accuracy": 0.9,
            "emissions_accuracy": 0.8
        }
    }
    
    response = await test_app.post("/api/v1/feedback", json=invalid_accuracy_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

async def test_feedback_handler(test_data, mock_db):
    """Test the FeedbackHandler class."""
    handler = FeedbackHandler()
    
    # Test submitting feedback
    feedback = RouteFeedback(
        route_id="test_route_1",
        user_id="test_user_1",
        rating=4,
        accuracy={
            "traffic_accuracy": 0.85,
            "weather_accuracy": 0.9,
            "emissions_accuracy": 0.8
        },
        comments="Good route suggestion",
        suggestions=["Add more alternative routes"]
    )
    
    await handler.submit_feedback(feedback)
    
    # Test retrieving feedback
    route_feedback = await handler.get_route_feedback("test_route_1")
    assert len(route_feedback) > 0
    assert isinstance(route_feedback[0], RouteFeedback)
    
    # Test generating analytics
    analytics = await handler.generate_analytics()
    assert isinstance(analytics, FeedbackAnalytics)
    assert analytics.average_rating > 0
    assert all(0 <= v <= 1 for v in analytics.accuracy_metrics.values())

async def test_feedback_aggregation(test_data, mock_db):
    """Test feedback aggregation functionality."""
    handler = FeedbackHandler()
    
    # Submit multiple feedback entries
    feedbacks = [
        RouteFeedback(
            route_id="test_route_1",
            user_id=f"test_user_{i}",
            rating=i % 5 + 1,
            accuracy={
                "traffic_accuracy": 0.8 + (i % 3) * 0.1,
                "weather_accuracy": 0.85 + (i % 3) * 0.05,
                "emissions_accuracy": 0.75 + (i % 3) * 0.1
            },
            comments=f"Feedback {i}",
            suggestions=[f"Suggestion {i}"]
        )
        for i in range(5)
    ]
    
    for feedback in feedbacks:
        await handler.submit_feedback(feedback)
    
    # Get aggregated analytics
    analytics = await handler.generate_analytics()
    
    # Assertions
    assert analytics.average_rating == pytest.approx(3.0, rel=0.1)
    assert len(analytics.common_suggestions) > 0
    assert all(0.7 <= v <= 1.0 for v in analytics.accuracy_metrics.values())

async def test_feedback_filtering(test_data, mock_db):
    """Test feedback filtering functionality."""
    handler = FeedbackHandler()
    
    # Get feedback with filters
    recent_feedback = await handler.get_route_feedback(
        route_id="test_route_1",
        min_rating=4,
        start_date="2024-01-01",
        end_date="2024-12-31"
    )
    
    # Assertions
    assert all(feedback.rating >= 4 for feedback in recent_feedback)
    assert all(isinstance(feedback, RouteFeedback) for feedback in recent_feedback)

async def test_feedback_export(test_app):
    """Test feedback export functionality."""
    # Make request for CSV export
    response = await test_app.get("/api/v1/feedback/export?format=csv")
    
    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "text/csv"
    content = response.content.decode()
    assert "route_id,user_id,rating" in content
    
    # Make request for JSON export
    response = await test_app.get("/api/v1/feedback/export?format=json")
    
    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert isinstance(data, list)
    assert all(isinstance(feedback, dict) for feedback in data) 