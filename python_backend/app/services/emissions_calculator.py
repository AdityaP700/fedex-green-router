from typing import Dict, List
from models.vehicle import Vehicle
from models.route import Route

class EmissionsCalculator:
    def __init__(self):
        # Emission factors for different vehicle types (g CO2/km)
        self.emission_factors = {
            "light_duty": 147,  # Light-duty vehicle
            "medium_duty": 271,  # Medium-duty truck
            "heavy_duty": 857,  # Heavy-duty truck
            "electric": 0,      # Electric vehicle
            "hybrid": 92       # Hybrid vehicle
        }

    def calculate_route_emissions(
        self,
        route: Route,
        vehicle: Vehicle,
        weather_conditions: Dict,
        traffic_conditions: Dict
    ) -> Dict:
        """Calculate total emissions for a given route."""
        base_emissions = self._calculate_base_emissions(route, vehicle)
        
        # Apply weather impact factor
        weather_factor = self._calculate_weather_impact(weather_conditions)
        
        # Apply traffic impact factor
        traffic_factor = self._calculate_traffic_impact(traffic_conditions)
        
        # Calculate total emissions with all factors
        total_emissions = base_emissions * weather_factor * traffic_factor
        
        return {
            "total_emissions_kg": total_emissions / 1000,  # Convert g to kg
            "base_emissions_kg": base_emissions / 1000,
            "weather_factor": weather_factor,
            "traffic_factor": traffic_factor,
            "route_length_km": route.total_distance,
            "vehicle_type": vehicle.type
        }

    def _calculate_base_emissions(self, route: Route, vehicle: Vehicle) -> float:
        """Calculate base emissions without external factors."""
        emission_factor = self.emission_factors.get(vehicle.type, self.emission_factors["medium_duty"])
        return route.total_distance * emission_factor

    def _calculate_weather_impact(self, weather_conditions: Dict) -> float:
        """Calculate weather impact factor on emissions."""
        # Default factor is 1.0 (no impact)
        factor = 1.0
        
        # Adjust for temperature
        temperature = weather_conditions.get("temp", 20)
        if temperature < 0:
            factor *= 1.2  # Cold weather increases emissions
        elif temperature > 30:
            factor *= 1.1  # Hot weather increases emissions
        
        # Adjust for precipitation
        if weather_conditions.get("rain", 0) > 0:
            factor *= 1.15  # Rain increases emissions
        
        if weather_conditions.get("snow", 0) > 0:
            factor *= 1.25  # Snow significantly increases emissions
        
        return factor

    def _calculate_traffic_impact(self, traffic_conditions: Dict) -> float:
        """Calculate traffic impact factor on emissions."""
        # Default factor is 1.0 (no impact)
        factor = 1.0
        
        # Adjust based on congestion level
        congestion_level = traffic_conditions.get("congestion_level", 0)
        
        if congestion_level > 80:
            factor *= 1.5  # Heavy traffic
        elif congestion_level > 50:
            factor *= 1.3  # Moderate traffic
        elif congestion_level > 20:
            factor *= 1.1  # Light traffic
        
        return factor

    def get_emission_reduction_suggestions(
        self,
        route: Route,
        vehicle: Vehicle,
        current_emissions: Dict
    ) -> List[Dict]:
        """Generate suggestions for reducing emissions."""
        suggestions = []
        
        # Check if alternative vehicle type would help
        for vehicle_type, emission_factor in self.emission_factors.items():
            if vehicle_type != vehicle.type:
                potential_savings = (
                    (self.emission_factors[vehicle.type] - emission_factor)
                    * route.total_distance
                    / 1000  # Convert to kg
                )
                if potential_savings > 0:
                    suggestions.append({
                        "type": "vehicle_change",
                        "suggestion": f"Consider using a {vehicle_type} vehicle",
                        "potential_savings_kg": potential_savings
                    })
        
        # Add time-based suggestions
        if current_emissions["traffic_factor"] > 1.2:
            suggestions.append({
                "type": "timing",
                "suggestion": "Consider rescheduling to avoid peak traffic hours",
                "potential_savings_kg": current_emissions["total_emissions_kg"] * 0.2
            })
        
        return suggestions
