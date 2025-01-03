from fastapi import Request
from fastapi.responses import JSONResponse
from .exceptions import FedExGreenRouterError, ValidationError, AuthenticationError, ResourceNotFoundError
from monitoring.metrics_collector import MetricsCollector

metrics_collector = MetricsCollector()

async def fedex_error_handler(request: Request, exc: FedExGreenRouterError) -> JSONResponse:
    """Handle FedEx Green Router specific errors."""
    await metrics_collector.record_error(str(exc), exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "status_code": exc.status_code
        }
    )

async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle validation errors."""
    await metrics_collector.record_error("Validation Error", 400)
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation Error",
            "details": exc.details,
            "message": exc.message
        }
    )

async def authentication_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
    """Handle authentication errors."""
    await metrics_collector.record_error("Authentication Error", 401)
    return JSONResponse(
        status_code=401,
        content={
            "error": "Authentication Error",
            "message": exc.message
        }
    )

async def not_found_error_handler(request: Request, exc: ResourceNotFoundError) -> JSONResponse:
    """Handle resource not found errors."""
    await metrics_collector.record_error("Resource Not Found", 404)
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": exc.message
        }
    ) 