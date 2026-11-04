from fastapi import APIRouter, Request

from ..schemas import HealthResponse

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
def get_health(request: Request) -> HealthResponse:
    app_state = request.app.state
    model_name = getattr(app_state, "model_name", "unknown")
    sentiment_model = getattr(app_state, "sentiment_model", None)

    is_mock = False
    model_loaded = True
    if sentiment_model is not None:
        if hasattr(sentiment_model, "is_mock"):
            is_mock = bool(sentiment_model.is_mock)
        else:
            is_mock = (model_name == "mock")

    queue = getattr(app_state, "priority_queue", None)
    queue_size = queue.size() if queue else 0

    return HealthResponse(
        status="ok",
        version="0.1.0",
        model_name=model_name,
        is_mock=is_mock,
        model_loaded=model_loaded,
        queue_size=queue_size,
    )
