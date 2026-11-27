"""AI Sentiment, Priority Queue, and Storefront-to-Triage gateway ports."""

from datetime import datetime
from typing import Any, Protocol, runtime_checkable

from ...core.queue.priority_queue import QueueItem
from ...core.sentiment.base import AbsaResult
from ..entities import TriageDispatchRequest, TriageDispatchResult


@runtime_checkable
class SentimentAnalyzerPort(Protocol):
    def predict(self, text: str, candidates: list[str] | None = None) -> AbsaResult:
        ...


@runtime_checkable
class PriorityQueuePort(Protocol):
    def push(
        self,
        ticket_id: int,
        priority_score: float,
        created_at: datetime,
        data: Any = None,
    ) -> None:
        ...

    def pop(self) -> QueueItem | None:
        ...

    def peek(self) -> QueueItem | None:
        ...

    def remove(self, ticket_id: int) -> bool:
        ...

    def size(self) -> int:
        ...

    def to_sorted_list(self) -> list[QueueItem]:
        ...


@runtime_checkable
class TriageGatewayPort(Protocol):
    """Decouples Storefront review submission from Triage ML/Queue execution.

    Implementations:
    - LocalTriageGateway: in-process execution inside Modular Monolith.
    - HttpTriageGateway: remote HTTP call to an independent Triage microservice.
    """

    def dispatch_ticket(self, request: TriageDispatchRequest) -> TriageDispatchResult:
        ...
