"""Remote HTTP TriageGatewayPort adapter for split-service deployments."""

from typing import Any

import httpx

from ...domain.entities import (
    AspectObservation,
    TriageDispatchRequest,
    TriageDispatchResult,
)
from ...domain.exceptions import DomainError


class HttpTriageGateway:
    """Sends ticket content over HTTP POST to an external Triage API service.

    Activated simply by setting TRIAGE_GATEWAY_MODE=http and TRIAGE_API_URL in .env
    without modifying any Storefront Application Service code (SOLID-D).
    """

    def __init__(
        self,
        base_url: str,
        api_token: str = "",
        timeout_seconds: float = 30.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_token = api_token.strip()
        self._timeout = timeout_seconds
        self._http_client = http_client

    def dispatch_ticket(self, request: TriageDispatchRequest) -> TriageDispatchResult:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._api_token:
            headers["Authorization"] = f"Bearer {self._api_token}"

        payload: dict[str, Any] = {
            "content": request.content,
            "source": request.source,
            "product_id": request.product_id,
            "product_name": request.product_name,
            "product_slug": request.product_slug,
            "user_id": request.user_id,
            "author_name": request.author_name,
        }
        url = f"{self._base_url}/api/v1/tickets"

        try:
            if self._http_client is not None:
                response = self._http_client.post(url, json=payload, headers=headers)
            else:
                with httpx.Client(timeout=self._timeout) as client:
                    response = client.post(url, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            raise DomainError(f"Không thể kết nối tới dịch vụ AI Triage: {exc}") from exc

        if response.status_code >= 400:
            raise DomainError(
                f"Dịch vụ AI Triage từ chối xử lý (HTTP {response.status_code}): {response.text}"
            )

        data: dict[str, Any] = response.json()
        raw_aspects = data.get("aspects") or []
        aspects = tuple(
            AspectObservation(
                aspect=str(item["aspect"]),
                sentiment=str(item["sentiment"]),
                confidence=float(item["confidence"]),
                terms=tuple(item.get("terms") or ()),
            )
            for item in raw_aspects
        )
        return TriageDispatchResult(
            ticket_id=int(data["id"]),
            sentiment_label=data.get("sentiment_label"),
            confidence=(
                float(data["confidence"]) if data.get("confidence") is not None else None
            ),
            priority_score=float(data.get("priority_score", 0.0)),
            priority_level=str(data.get("priority_level", "LOW")),
            dominant_aspect=data.get("dominant_aspect"),
            needs_manual_review=bool(data.get("needs_manual_review", False)),
            aspects=aspects,
        )
