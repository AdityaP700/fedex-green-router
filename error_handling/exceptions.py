from typing import Any, Optional

class FedExGreenRouterError(Exception):
    """Base exception class for FedEx Green Router."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

class ValidationError(FedExGreenRouterError):
    """Raised when input validation fails."""
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, status_code=400, details=details)

class AuthenticationError(FedExGreenRouterError):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class ResourceNotFoundError(FedExGreenRouterError):
    """Raised when a requested resource is not found."""
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with id {resource_id} not found"
        super().__init__(message, status_code=404)

class ExternalAPIError(FedExGreenRouterError):
    """Raised when an external API call fails."""
    def __init__(self, api_name: str, message: str, details: Optional[Any] = None):
        super().__init__(
            f"Error calling {api_name} API: {message}",
            status_code=502,
            details=details
        ) 