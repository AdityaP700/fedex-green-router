import pytest
import numpy as np
from ml_layer.route_predictor import RoutePredictor
from models.route import Route, RoutePoint, RouteSegment
from models.vehicle import Vehicle

async def test_model_training(test_data, mock_db):
    """Test training the prediction models."""
    predictor = RoutePredictor()
    
    # Generate synthetic training data
    routes = []
    for i in range(100):
        route = Route(
            id=f"train_route_{i}",
            start_point=RoutePoint(lat=40.7128, lon=-74.0060),
            end_point=RoutePoint(lat=40.7614, lon=-73.9776),
            total_distance=5.0 + np.random.normal(0, 0.5),
            total_duration=15.0 + np.random.normal(0, 2.0),
            total_emissions=0.75 + np.random.normal(0, 0.1),
            segments=[
                RouteSegment(
                    start_point=RoutePoint(lat=40.7128, lon=-74.0060),
                    end_point=RoutePoint(lat=40.7614, lon=-73.9776),
                    distance=5.0 + np.random.normal(0, 0.5),
                    duration=15.0 + np.random.normal(0, 2.0)
                )
            ],
            traffic_level="medium",
            weather_condition="clear"
        )
        routes.append(route)
    
    # Train models
    await predictor.train_models(routes)
    
    # Assertions
    assert predictor.traffic_model is not None
    assert predictor.emissions_model is not None
    assert predictor.duration_model is not None

async def test_route_prediction(test_data):
    """Test predicting route metrics."""
    predictor = RoutePredictor()
    
    # Test data
    vehicle = Vehicle(**test_data["vehicles"][0])
    start_point = RoutePoint(lat=40.7128, lon=-74.0060)
    end_point = RoutePoint(lat=40.7614, lon=-73.9776)
    
    # Make predictions
    predictions = await predictor.predict_route_metrics(
        vehicle=vehicle,
        start_point=start_point,
        end_point=end_point,
        hour=14,
        day_of_week=2,
        temperature=20,
        precipitation=0,
        wind_speed=10
    )
    
    # Assertions
    assert "traffic_delay" in predictions
    assert "emissions" in predictions
    assert "duration" in predictions
    assert all(isinstance(v, float) for v in predictions.values())
    assert all(v >= 0 for v in predictions.values())

async def test_model_update(test_data):
    """Test updating the models with new data."""
    predictor = RoutePredictor()
    
    # Initial route data
    initial_route = Route(
        id="update_route_1",
        start_point=RoutePoint(lat=40.7128, lon=-74.0060),
        end_point=RoutePoint(lat=40.7614, lon=-73.9776),
        total_distance=5.2,
        total_duration=15.5,
        total_emissions=0.75,
        segments=[
            RouteSegment(
                start_point=RoutePoint(lat=40.7128, lon=-74.0060),
                end_point=RoutePoint(lat=40.7614, lon=-73.9776),
                distance=5.2,
                duration=15.5
            )
        ],
        traffic_level="low",
        weather_condition="clear"
    )
    
    # Update models
    await predictor.update_models([initial_route])
    
    # Make predictions before and after update
    vehicle = Vehicle(**test_data["vehicles"][0])
    start_point = RoutePoint(lat=40.7128, lon=-74.0060)
    end_point = RoutePoint(lat=40.7614, lon=-73.9776)
    
    predictions_before = await predictor.predict_route_metrics(
        vehicle=vehicle,
        start_point=start_point,
        end_point=end_point,
        hour=14,
        day_of_week=2,
        temperature=20,
        precipitation=0,
        wind_speed=10
    )
    
    # Add new route with different conditions
    new_route = Route(
        id="update_route_2",
        start_point=RoutePoint(lat=40.7128, lon=-74.0060),
        end_point=RoutePoint(lat=40.7614, lon=-73.9776),
        total_distance=5.2,
        total_duration=20.5,  # Higher duration due to traffic
        total_emissions=0.9,  # Higher emissions
        segments=[
            RouteSegment(
                start_point=RoutePoint(lat=40.7128, lon=-74.0060),
                end_point=RoutePoint(lat=40.7614, lon=-73.9776),
                distance=5.2,
                duration=20.5
            )
        ],
        traffic_level="high",
        weather_condition="rain"
    )
    
    await predictor.update_models([new_route])
    
    predictions_after = await predictor.predict_route_metrics(
        vehicle=vehicle,
        start_point=start_point,
        end_point=end_point,
        hour=14,
        day_of_week=2,
        temperature=20,
        precipitation=1,  # Rainy conditions
        wind_speed=10
    )
    
    # Assertions
    assert predictions_after["traffic_delay"] > predictions_before["traffic_delay"]
    assert predictions_after["emissions"] > predictions_before["emissions"]
    assert predictions_after["duration"] > predictions_before["duration"]

async def test_confidence_scores(test_data):
    """Test confidence score calculation for predictions."""
    predictor = RoutePredictor()
    
    # Test data
    vehicle = Vehicle(**test_data["vehicles"][0])
    start_point = RoutePoint(lat=40.7128, lon=-74.0060)
    end_point = RoutePoint(lat=40.7614, lon=-73.9776)
    
    # Get predictions with confidence scores
    predictions = await predictor.predict_route_metrics(
        vehicle=vehicle,
        start_point=start_point,
        end_point=end_point,
        hour=14,
        day_of_week=2,
        temperature=20,
        precipitation=0,
        wind_speed=10,
        return_confidence=True
    )
    
    # Assertions
    assert "traffic_confidence" in predictions
    assert "emissions_confidence" in predictions
    assert "duration_confidence" in predictions
    assert all(0 <= score <= 1 for score in [
        predictions["traffic_confidence"],
        predictions["emissions_confidence"],
        predictions["duration_confidence"]
    ])

async def test_feature_importance(test_data):
    """Test feature importance analysis."""
    predictor = RoutePredictor()
    
    # Train models with some data
    routes = []
    for i in range(100):
        route = Route(
            id=f"importance_route_{i}",
            start_point=RoutePoint(lat=40.7128, lon=-74.0060),
            end_point=RoutePoint(lat=40.7614, lon=-73.9776),
            total_distance=5.0 + np.random.normal(0, 0.5),
            total_duration=15.0 + np.random.normal(0, 2.0),
            total_emissions=0.75 + np.random.normal(0, 0.1),
            segments=[
                RouteSegment(
                    start_point=RoutePoint(lat=40.7128, lon=-74.0060),
                    end_point=RoutePoint(lat=40.7614, lon=-73.9776),
                    distance=5.0 + np.random.normal(0, 0.5),
                    duration=15.0 + np.random.normal(0, 2.0)
                )
            ],
            traffic_level="medium",
            weather_condition="clear"
        )
        routes.append(route)
    
    await predictor.train_models(routes)
    
    # Get feature importance
    importance = predictor.get_feature_importance()
    
    # Assertions
    assert "traffic_model" in importance
    assert "emissions_model" in importance
    assert "duration_model" in importance
    assert all(isinstance(imp, dict) for imp in importance.values())
    assert all(sum(model_imp.values()) == pytest.approx(1.0) 
              for model_imp in importance.values()) 