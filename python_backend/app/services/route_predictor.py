from typing import List, Dict, Optional
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import pandas as pd
from datetime import datetime, time
from models.route import Route, RoutePoint
from models.vehicle import Vehicle

class RoutePredictor:
    def __init__(self):
        self.traffic_model = None
        self.emissions_model = None
        self.duration_model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'hour', 'day_of_week', 'is_holiday', 'distance_km',
            'vehicle_type', 'vehicle_load_ratio', 'temperature',
            'precipitation', 'wind_speed', 'air_quality_index'
        ]

    def train_models(self, historical_data: pd.DataFrame):
        """Train prediction models using historical route data."""
        X = self._prepare_features(historical_data)
        
        # Train traffic prediction model
        y_traffic = historical_data['traffic_delay']
        self.traffic_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.traffic_model.fit(X, y_traffic)
        
        # Train emissions prediction model
        y_emissions = historical_data['total_emissions']
        self.emissions_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.emissions_model.fit(X, y_emissions)
        
        # Train duration prediction model
        y_duration = historical_data['total_duration']
        self.duration_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.duration_model.fit(X, y_duration)

    def predict_route_metrics(
        self,
        route: Route,
        vehicle: Vehicle,
        weather_data: Dict,
        aqi_data: Dict,
        current_time: Optional[datetime] = None
    ) -> Dict:
        """Predict traffic, emissions, and duration for a route."""
        if not all([self.traffic_model, self.emissions_model, self.duration_model]):
            raise ValueError("Models not trained. Call train_models first.")
        
        # Prepare features for prediction
        features = self._extract_features(
            route, vehicle, weather_data, aqi_data, current_time or datetime.now()
        )
        X = self.scaler.transform(features.reshape(1, -1))
        
        # Make predictions
        traffic_delay = float(self.traffic_model.predict(X)[0])
        emissions = float(self.emissions_model.predict(X)[0])
        duration = float(self.duration_model.predict(X)[0])
        
        return {
            "predicted_traffic_delay": traffic_delay,
            "predicted_emissions": emissions,
            "predicted_duration": duration,
            "confidence_scores": self._calculate_confidence_scores(X)
        }

    def update_models(self, new_data: pd.DataFrame):
        """Update models with new route data."""
        X = self._prepare_features(new_data)
        
        # Update traffic model
        y_traffic = new_data['traffic_delay']
        if self.traffic_model:
            # Incremental update for traffic model
            self.traffic_model.n_estimators += 10
            additional_estimators = RandomForestRegressor(n_estimators=10, random_state=42)
            additional_estimators.fit(X, y_traffic)
            self.traffic_model.estimators_ += additional_estimators.estimators_
        else:
            self.traffic_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.traffic_model.fit(X, y_traffic)
        
        # Similar updates for emissions and duration models
        y_emissions = new_data['total_emissions']
        if self.emissions_model:
            self.emissions_model.n_estimators += 10
            additional_estimators = RandomForestRegressor(n_estimators=10, random_state=42)
            additional_estimators.fit(X, y_emissions)
            self.emissions_model.estimators_ += additional_estimators.estimators_
        else:
            self.emissions_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.emissions_model.fit(X, y_emissions)
        
        y_duration = new_data['total_duration']
        if self.duration_model:
            self.duration_model.n_estimators += 10
            additional_estimators = RandomForestRegressor(n_estimators=10, random_state=42)
            additional_estimators.fit(X, y_duration)
            self.duration_model.estimators_ += additional_estimators.estimators_
        else:
            self.duration_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.duration_model.fit(X, y_duration)

    def save_models(self, path: str):
        """Save trained models to disk."""
        if not all([self.traffic_model, self.emissions_model, self.duration_model]):
            raise ValueError("Models not trained. Cannot save untrained models.")
        
        joblib.dump(self.traffic_model, f"{path}/traffic_model.joblib")
        joblib.dump(self.emissions_model, f"{path}/emissions_model.joblib")
        joblib.dump(self.duration_model, f"{path}/duration_model.joblib")
        joblib.dump(self.scaler, f"{path}/scaler.joblib")

    def load_models(self, path: str):
        """Load trained models from disk."""
        self.traffic_model = joblib.load(f"{path}/traffic_model.joblib")
        self.emissions_model = joblib.load(f"{path}/emissions_model.joblib")
        self.duration_model = joblib.load(f"{path}/duration_model.joblib")
        self.scaler = joblib.load(f"{path}/scaler.joblib")

    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare feature matrix from historical data."""
        X = data[self.feature_columns].copy()
        
        # Convert categorical variables
        X['vehicle_type'] = X['vehicle_type'].map({
            'light_duty': 0,
            'medium_duty': 1,
            'heavy_duty': 2,
            'electric': 3,
            'hybrid': 4
        })
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled

    def _extract_features(
        self,
        route: Route,
        vehicle: Vehicle,
        weather_data: Dict,
        aqi_data: Dict,
        current_time: datetime
    ) -> np.ndarray:
        """Extract features for prediction."""
        features = np.zeros(len(self.feature_columns))
        
        # Time-based features
        features[0] = current_time.hour
        features[1] = current_time.weekday()
        features[2] = self._is_holiday(current_time)
        
        # Route features
        features[3] = route.total_distance
        
        # Vehicle features
        vehicle_type_map = {
            'light_duty': 0,
            'medium_duty': 1,
            'heavy_duty': 2,
            'electric': 3,
            'hybrid': 4
        }
        features[4] = vehicle_type_map.get(vehicle.type, 0)
        features[5] = (vehicle.current_load or 0) / vehicle.cargo_capacity
        
        # Weather features
        features[6] = weather_data.get('temp', 20)
        features[7] = weather_data.get('precipitation', 0)
        features[8] = weather_data.get('wind_speed', 0)
        
        # Air quality features
        features[9] = aqi_data.get('data', {}).get('aqi', 50)
        
        return features

    def _calculate_confidence_scores(self, X: np.ndarray) -> Dict[str, float]:
        """Calculate confidence scores for predictions."""
        # Use standard deviation of predictions across trees as confidence measure
        traffic_predictions = np.array([tree.predict(X) for tree in self.traffic_model.estimators_])
        emissions_predictions = np.array([tree.predict(X) for tree in self.emissions_model.estimators_])
        duration_predictions = np.array([tree.predict(X) for tree in self.duration_model.estimators_])
        
        return {
            "traffic_confidence": 1 - (np.std(traffic_predictions) / np.mean(traffic_predictions)),
            "emissions_confidence": 1 - (np.std(emissions_predictions) / np.mean(emissions_predictions)),
            "duration_confidence": 1 - (np.std(duration_predictions) / np.mean(duration_predictions))
        }

    def _is_holiday(self, date: datetime) -> int:
        """Determine if a date is a holiday."""
        # Implement holiday detection logic here
        # For now, just return 0 (not a holiday)
        return 0 