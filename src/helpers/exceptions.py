class IntegrationError(Exception):
    """Base exception class for integration errors."""

    pass


class AuthError(IntegrationError):
    """Raised when authentication or authorization fails."""

    pass


class RateLimitError(IntegrationError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, retry_after: int | None = None):
        self.retry_after = retry_after
        super().__init__(429, "Rate limit exceeded")


class NetworkError(IntegrationError):
    """Raised when network-related issues occur."""

    pass


class StateError(IntegrationError):
    """Raised when OAuth state validation fails."""

    pass


class DataError(IntegrationError):
    """Raised when there are issues with data format or validation."""

    pass
