"""Domain-level exceptions decoupled from HTTP / persistence frameworks."""


class DomainError(Exception):
    """Base error for all domain and application rule violations."""


class EntityNotFoundError(DomainError):
    """Raised when a requested aggregate or entity does not exist."""


class ConflictError(DomainError):
    """Raised when an operation violates a uniqueness or state conflict constraint."""


class AuthenticationError(DomainError):
    """Raised when credentials or access tokens are invalid or missing."""


class AuthorizationError(DomainError):
    """Raised when an authenticated actor lacks permission for an action."""


class ValidationDomainError(DomainError):
    """Raised when domain invariants on input data are violated."""
