from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.route_engine import router as route_router
from app.api.vehicle import router as vehicle_router
from app.api.metrics import router as metrics_router
from app.api.security import router as auth_router
from app.utils.error_handling.exceptions import (
    FedExGreenRouterError,
    ValidationError,
    AuthenticationError,
    ResourceNotFoundError
)
from app.utils.error_handling.handlers import (
    fedex_error_handler,
    validation_error_handler,
    authentication_error_handler,
    not_found_error_handler
)
from app.db.persistence import db

app = FastAPI(
    title="FedEx Green Router",
    description="Intelligent routing system with environmental considerations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "FedEx Green Router API",
        "version": "1.0.0",
        "description": "Intelligent routing system with environmental considerations",
        "endpoints": {
            "docs": "/docs",
            "routes": "/api/routes",
            "vehicles": "/api/vehicles",
            "metrics": "/api/metrics"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
