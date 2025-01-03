from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from route_engine.api import router as route_router
from route_engine.vehicle_api import router as vehicle_router
from route_engine.metrics_api import router as metrics_router
from security.auth_api import router as auth_router
from error_handling.exceptions import FedExGreenRouterError, ValidationError, AuthenticationError, ResourceNotFoundError
from error_handling.handlers import (
    fedex_error_handler,
    validation_error_handler,
    authentication_error_handler,
    not_found_error_handler
)
from persistence.db_handler import db

app = FastAPI(
    title="FedEx Green Router",
    description="Intelligent routing system with environmental considerations",
    version="1.0.0"
)

# Include routers
app.include_router(auth_router)  # Auth router doesn't require API key verification
app.include_router(route_router)
app.include_router(vehicle_router)
app.include_router(metrics_router)

# Add exception handlers
app.add_exception_handler(FedExGreenRouterError, fedex_error_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(AuthenticationError, authentication_error_handler)
app.add_exception_handler(ResourceNotFoundError, not_found_error_handler)

@app.on_event("startup")
async def startup_event():
    """Initialize database and create indexes on startup."""
    await db.init_db()
    
    # Create necessary indexes
    await db["api_keys"].create_index("key", unique=True)
    await db["api_keys"].create_index("client_id")
    await db["vehicles"].create_index("id", unique=True)
    await db["metrics"].create_index("request_id", unique=True)
    await db["metrics"].create_index("start_time")
    await db["errors"].create_index("timestamp")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
