"""Abstract Protocol ports enforcing the Dependency Inversion Principle (SOLID-D)."""

from .repositories import (
    CatalogRepositoryPort,
    ReviewRepositoryPort,
    TicketRepositoryPort,
    UserRepositoryPort,
)
from .security import PasswordHasherPort, TokenPayload, TokenProviderPort
from .storage import ImageStoragePort
from .triage import PriorityQueuePort, SentimentAnalyzerPort, TriageGatewayPort

__all__ = [
    "CatalogRepositoryPort",
    "ImageStoragePort",
    "PasswordHasherPort",
    "PriorityQueuePort",
    "ReviewRepositoryPort",
    "SentimentAnalyzerPort",
    "TicketRepositoryPort",
    "TokenPayload",
    "TokenProviderPort",
    "TriageGatewayPort",
    "UserRepositoryPort",
]
