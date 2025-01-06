import pytest
from unittest.mock import patch
from data_collection.collectors import (
    TrafficDataCollector,
    WeatherDataCollector,
    AirQualityDataCollector
)
from data_collection.models import (
    TrafficData,
    WeatherData,
    AirQualityData,
    Location
)

@pytest.fixture
def mock_tomtom_response():
    """Mock TomTom API response."""
    return {
        "flowSegmentData": {
            "currentSpeed": 35,
            "freeFlowSpeed": 45,
            "currentTravelTime": 300,
            "freeFlowTravelTime": 240,
            "confidence": 0.9,
            "roadClosure": False,
            "coordinates": {
                "coordinate": [
                    {"latitude": 40.7128, "longitude": -74.0060},
                    {"latitude": 40.7614, "longitude": -73.9776}
                ]
            }
        }
    }

@pytest.fixture
def mock_weather_response():
    """Mock OpenWeather API response."""
    return {
        "main": {
            "temp": 20,
            "humidity": 65,
            "pressure": 1013
        },
        "weather": [
            {
                "main": "Rain",
                "description": "light rain"
            }
        ],
        "wind": {
            "speed": 5.5,
            "deg": 180
        },
        "rain": {
            "1h": 0.5
        }
    }

@pytest.fixture
def mock_aqicn_response():
    """Mock AQICN API response."""
    return {
        "status": "ok",
        "data": {
            "aqi": 45,
            "iaqi": {
                "pm25": {"v": 15},
                "pm10": {"v": 25},
                "o3": {"v": 35},
                "no2": {"v": 20},
                "so2": {"v": 5},
                "co": {"v": 0.8}
            },
            "time": {
                "s": "2024-01-01 12:00:00"
            }
        }
    }

async def test_traffic_data_collection(mock_tomtom_response, mock_redis):
    """Test traffic data collection."""
    collector = TrafficDataCollector()
    
    with patch("data_collection.collectors.traffic.get_tomtom_data") as mock_get:
        mock_get.return_value = mock_tomtom_response
        
        # Collect traffic data
        traffic_data = await collector.collect_traffic_data(
            start=Location(lat=40.7128, lon=-74.0060),
            end=Location(lat=40.7614, lon=-73.9776)
        )
        
        # Assertions
        assert isinstance(traffic_data, TrafficData)
        assert traffic_data.current_speed == 35
        assert traffic_data.free_flow_speed == 45
        assert traffic_data.congestion_level == "medium"
        assert traffic_data.confidence == 0.9
        
        # Check caching
        cached_data = await mock_redis.get(
            "traffic:40.7128,-74.0060:40.7614,-73.9776"
        )
        assert cached_data is not None

async def test_weather_data_collection(mock_weather_response, mock_redis):
    """Test weather data collection."""
    collector = WeatherDataCollector()
    
    with patch("data_collection.collectors.weather.get_weather_data") as mock_get:
        mock_get.return_value = mock_weather_response
        
        # Collect weather data
        weather_data = await collector.collect_weather_data(
            location=Location(lat=40.7128, lon=-74.0060)
        )
        
        # Assertions
        assert isinstance(weather_data, WeatherData)
        assert weather_data.temperature == 20
        assert weather_data.condition == "Rain"
        assert weather_data.wind_speed == 5.5
        assert weather_data.precipitation == 0.5
        
        # Check caching
        cached_data = await mock_redis.get("weather:40.7128,-74.0060")
        assert cached_data is not None

async def test_air_quality_data_collection(mock_aqicn_response, mock_redis):
    """Test air quality data collection."""
    collector = AirQualityDataCollector()
    
    with patch("data_collection.collectors.air_quality.get_aqicn_data") as mock_get:
        mock_get.return_value = mock_aqicn_response
        
        # Collect air quality data
        air_quality_data = await collector.collect_air_quality_data(
            location=Location(lat=40.7128, lon=-74.0060)
        )
        
        # Assertions
        assert isinstance(air_quality_data, AirQualityData)
        assert air_quality_data.aqi == 45
        assert air_quality_data.pm25 == 15
        assert air_quality_data.pm10 == 25
        assert air_quality_data.ozone == 35
        
        # Check caching
        cached_data = await mock_redis.get("air_quality:40.7128,-74.0060")
        assert cached_data is not None

async def test_data_collection_error_handling():
    """Test error handling in data collection."""
    traffic_collector = TrafficDataCollector()
    weather_collector = WeatherDataCollector()
    air_quality_collector = AirQualityDataCollector()
    
    # Test traffic data collection error
    with patch("data_collection.collectors.traffic.get_tomtom_data") as mock_get:
        mock_get.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            await traffic_collector.collect_traffic_data(
                start=Location(lat=40.7128, lon=-74.0060),
                end=Location(lat=40.7614, lon=-73.9776)
            )
        assert "API Error" in str(exc_info.value)
    
    # Test weather data collection error
    with patch("data_collection.collectors.weather.get_weather_data") as mock_get:
        mock_get.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            await weather_collector.collect_weather_data(
                location=Location(lat=40.7128, lon=-74.0060)
            )
        assert "API Error" in str(exc_info.value)
    
    # Test air quality data collection error
    with patch("data_collection.collectors.air_quality.get_aqicn_data") as mock_get:
        mock_get.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            await air_quality_collector.collect_air_quality_data(
                location=Location(lat=40.7128, lon=-74.0060)
            )
        assert "API Error" in str(exc_info.value)

async def test_data_collection_rate_limiting(mock_redis):
    """Test rate limiting in data collection."""
    collector = TrafficDataCollector()
    
    # Set rate limit key
    await mock_redis.set("rate_limit:tomtom", "1")
    
    with pytest.raises(Exception) as exc_info:
        await collector.collect_traffic_data(
            start=Location(lat=40.7128, lon=-74.0060),
            end=Location(lat=40.7614, lon=-73.9776)
        )
    assert "Rate limit exceeded" in str(exc_info.value)

async def test_data_collection_cache_invalidation(mock_redis):
    """Test cache invalidation in data collection."""
    collector = WeatherDataCollector()
    
    with patch("data_collection.collectors.weather.get_weather_data") as mock_get:
        mock_get.return_value = mock_weather_response
        
        # Collect data first time
        weather_data_1 = await collector.collect_weather_data(
            location=Location(lat=40.7128, lon=-74.0060)
        )
        
        # Modify mock response
        mock_get.return_value = {
            **mock_weather_response,
            "main": {**mock_weather_response["main"], "temp": 25}
        }
        
        # Force cache invalidation
        await collector.invalidate_cache(
            location=Location(lat=40.7128, lon=-74.0060)
        )
        
        # Collect data again
        weather_data_2 = await collector.collect_weather_data(
            location=Location(lat=40.7128, lon=-74.0060)
        )
        
        # Assertions
        assert weather_data_1.temperature == 20
        assert weather_data_2.temperature == 25

async def test_data_collection_batch_processing():
    """Test batch processing of data collection."""
    collector = TrafficDataCollector()
    
    locations = [
        (
            Location(lat=40.7128, lon=-74.0060),
            Location(lat=40.7614, lon=-73.9776)
        ),
        (
            Location(lat=40.7614, lon=-73.9776),
            Location(lat=40.7505, lon=-73.9934)
        )
    ]
    
    with patch("data_collection.collectors.traffic.get_tomtom_data") as mock_get:
        mock_get.return_value = mock_tomtom_response
        
        # Collect traffic data in batch
        traffic_data = await collector.collect_traffic_data_batch(locations)
        
        # Assertions
        assert len(traffic_data) == 2
        assert all(isinstance(data, TrafficData) for data in traffic_data)
        assert mock_get.call_count == 2 