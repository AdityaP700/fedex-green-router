from fastapi import HTTPException
from typing import Dict, Any
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class ErrorHandler:
    @staticmethod
    async def handle_error(error: Exception) -> Dict[str, Any]:
        """Handle different types of errors and return appropriate responses"""
        if isinstance(error, HTTPException):
            logger.error(f"HTTP Exception: {error.detail}")
            return {
                "error": error.detail,
                "status_code": error.status_code,
                "type": "http_error"
            }
        if isinstance(error, ValueError):
            logger.error(f"Value Error: {str(error)}")
            return {
                "error": str(error),
                "status_code": 400,
                "type": "validation_error"
            }
        # Database errors
        if "MongoClient" in str(error.__class__):
            logger.error(f"Database Error: {str(error)}")
            return {
                "error": "Database operation failed",
                "status_code": 503,
                "type": "database_error"
            }
        # API errors
        if "APIError" in str(error.__class__):
            logger.error(f"External API Error: {str(error)}")
            return {
                "error": "External service unavailable",
                "status_code": 502,
                "type": "api_error"
            }
        # Default error handler
        logger.error(f"Unexpected Error: {str(error)}")
        return {
            "error": "Internal server error",
            "status_code": 500,
            "type": "internal_error"
        }
    @staticmethod
    async def log_error(error: Exception, context: dict = None):
        """Log error with context for debugging"""
        error_context = {
            "error_type": error.__class__.__name__,
            "error_message": str(error),
            "context": context or {}
        }
        logger.error(f"Error occurred: {error_context}")
