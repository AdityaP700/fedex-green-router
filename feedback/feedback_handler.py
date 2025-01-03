from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from models.route import Route
from models.vehicle import Vehicle
from persistence.db_handler import db

class RouteFeedback(BaseModel):
    """Model for route feedback data."""
    route_id: str = Field(..., description="Unique identifier for the route")
    user_id: str = Field(..., description="User who provided the feedback")
    vehicle_id: str = Field(..., description="Vehicle used for the route")
    rating: int = Field(..., ge=1, le=5, description="Route rating (1-5)")
    actual_duration: Optional[float] = Field(None, description="Actual route duration in minutes")
    actual_emissions: Optional[float] = Field(None, description="Actual emissions in kg CO2")
    traffic_accuracy: Optional[int] = Field(None, ge=1, le=5, description="Traffic prediction accuracy (1-5)")
    weather_impact: Optional[int] = Field(None, ge=1, le=5, description="Weather impact rating (1-5)")
    comments: Optional[str] = Field(None, description="Additional comments")
    timestamp: datetime = Field(default_factory=datetime.now)

class FeedbackAnalytics(BaseModel):
    """Model for feedback analytics."""
    average_rating: float
    total_feedback_count: int
    rating_distribution: Dict[int, int]
    traffic_accuracy_score: float
    weather_impact_score: float
    common_issues: List[str]
    improvement_suggestions: List[str]

class FeedbackHandler:
    """Handler for processing and analyzing route feedback."""
    
    @staticmethod
    async def submit_feedback(feedback: RouteFeedback) -> Dict:
        """Submit new feedback for a route."""
        try:
            # Store feedback in database
            feedback_dict = feedback.dict()
            await db.insert_one("route_feedback", feedback_dict)
            
            # Update route statistics
            await FeedbackHandler._update_route_stats(feedback)
            
            # Trigger ML model update if needed
            await FeedbackHandler._check_and_trigger_model_update(feedback)
            
            return {
                "status": "success",
                "message": "Feedback submitted successfully",
                "feedback_id": str(feedback_dict.get("_id"))
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to submit feedback: {str(e)}"
            }

    @staticmethod
    async def get_route_feedback(route_id: str) -> List[RouteFeedback]:
        """Get all feedback for a specific route."""
        feedback_data = await db.find("route_feedback", {"route_id": route_id})
        return [RouteFeedback(**data) for data in feedback_data]

    @staticmethod
    async def get_analytics(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> FeedbackAnalytics:
        """Get analytics for feedback within a date range."""
        query = {}
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        feedback_data = await db.find("route_feedback", query)
        
        # Calculate analytics
        ratings = [f["rating"] for f in feedback_data]
        traffic_scores = [f["traffic_accuracy"] for f in feedback_data if f.get("traffic_accuracy")]
        weather_scores = [f["weather_impact"] for f in feedback_data if f.get("weather_impact")]
        
        # Calculate rating distribution
        rating_dist = {i: ratings.count(i) for i in range(1, 6)}
        
        # Analyze comments for common issues and suggestions
        issues, suggestions = await FeedbackHandler._analyze_comments(feedback_data)
        
        return FeedbackAnalytics(
            average_rating=sum(ratings) / len(ratings) if ratings else 0,
            total_feedback_count=len(feedback_data),
            rating_distribution=rating_dist,
            traffic_accuracy_score=sum(traffic_scores) / len(traffic_scores) if traffic_scores else 0,
            weather_impact_score=sum(weather_scores) / len(weather_scores) if weather_scores else 0,
            common_issues=issues,
            improvement_suggestions=suggestions
        )

    @staticmethod
    async def _update_route_stats(feedback: RouteFeedback):
        """Update route statistics based on feedback."""
        stats = await db.find_one("route_stats", {"route_id": feedback.route_id})
        
        if stats:
            # Update existing stats
            total_ratings = stats["total_ratings"] + 1
            new_avg_rating = (
                (stats["average_rating"] * stats["total_ratings"] + feedback.rating)
                / total_ratings
            )
            
            await db.update_one(
                "route_stats",
                {"route_id": feedback.route_id},
                {
                    "$set": {
                        "average_rating": new_avg_rating,
                        "total_ratings": total_ratings,
                        "last_feedback": feedback.timestamp
                    },
                    "$push": {
                        "recent_feedback": {
                            "$each": [feedback.dict()],
                            "$slice": -10  # Keep only last 10 feedback entries
                        }
                    }
                }
            )
        else:
            # Create new stats document
            await db.insert_one(
                "route_stats",
                {
                    "route_id": feedback.route_id,
                    "average_rating": feedback.rating,
                    "total_ratings": 1,
                    "last_feedback": feedback.timestamp,
                    "recent_feedback": [feedback.dict()]
                }
            )

    @staticmethod
    async def _check_and_trigger_model_update(feedback: RouteFeedback):
        """Check if ML model update is needed and trigger if necessary."""
        # Get recent feedback count
        recent_count = await db.count(
            "route_feedback",
            {
                "timestamp": {
                    "$gte": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                }
            }
        )
        
        # Trigger update if we have enough new feedback
        if recent_count >= 100:  # Arbitrary threshold
            await FeedbackHandler._trigger_model_update()

    @staticmethod
    async def _trigger_model_update():
        """Trigger ML model update based on feedback data."""
        # Get all relevant feedback data
        feedback_data = await db.find(
            "route_feedback",
            {"actual_duration": {"$exists": True}, "actual_emissions": {"$exists": True}}
        )
        
        # Prepare training data
        training_data = []
        for feedback in feedback_data:
            route_data = await db.find_one("routes", {"route_id": feedback["route_id"]})
            vehicle_data = await db.find_one("vehicles", {"vehicle_id": feedback["vehicle_id"]})
            
            if route_data and vehicle_data:
                training_data.append({
                    "actual_duration": feedback["actual_duration"],
                    "actual_emissions": feedback["actual_emissions"],
                    "predicted_duration": route_data["predicted_duration"],
                    "predicted_emissions": route_data["predicted_emissions"],
                    "route_distance": route_data["total_distance"],
                    "vehicle_type": vehicle_data["type"],
                    "weather_conditions": route_data["weather_conditions"],
                    "traffic_conditions": route_data["traffic_conditions"]
                })
        
        if training_data:
            # Trigger ML model update
            # This should be implemented as an async task
            pass

    @staticmethod
    async def _analyze_comments(feedback_data: List[Dict]) -> tuple[List[str], List[str]]:
        """Analyze feedback comments for common issues and suggestions."""
        # Implement NLP-based analysis here
        # For now, return placeholder data
        return (
            ["Traffic prediction accuracy", "Weather impact assessment"],
            ["Improve real-time updates", "Add alternative route suggestions"]
        ) 