class FedExGreenRouterError(Exception):
    """Base exception for FedEx Green Router."""
    pass

class ValidationError(FedExGreenRouterError):
    """Raised when input validation fails."""
    pass

class AuthenticationError(FedExGreenRouterError):
    """Raised when authentication fails."""
    pass

class ResourceNotFoundError(FedExGreenRouterError):
    """Raised when a requested resource is not found."""
    pass 