from fastapi import Request
from fastapi.responses import JSONResponse
from .exceptions import FedExGreenRouterError, ValidationError, AuthenticationError, ResourceNotFoundError

async def fedex_error_handler(request: Request, exc: FedExGreenRouterError):
    return JSONResponse(
        status_code=500,
        content={"message": str(exc)},
    )

async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)},
    )

async def authentication_error_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=401,
        content={"message": str(exc)},
    )

async def not_found_error_handler(request: Request, exc: ResourceNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"message": str(exc)},
    ) 