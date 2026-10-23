from fastapi import APIRouter, Request

from ..schemas import HealthResponse

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
def get_health(request: Request) -> HealthResponse:
    app_state = request.app.state
    model_name = getattr(app_state, "model_name", "unknown")
    queue = getattr(app_state, "priority_queue", None)
    queue_size = queue.size() if queue else 0

    return HealthResponse(
        status="ok",
        version="0.1.0",
        model_name=model_name,
        queue_size=queue_size,
    )
