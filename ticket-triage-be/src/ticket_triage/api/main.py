import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..settings import settings
from ..db.session import engine, SessionLocal
from ..db.init_db import init_db
from ..db.repository import TicketRepository
from ..core.taxonomy import Taxonomy
from ..core.queue.priority_queue import TicketPriorityQueue
from ..core.sentiment.mock import MockSentimentModel
from ..core.sentiment.baseline import ZeroShotNliModel
from .routers import health, meta, tickets, stats

logger = logging.getLogger("ticket_triage")
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Khởi tạo CSDL SQLite (bật WAL mode, tạo bảng)
    logger.info("Initializing SQLite database with WAL mode...")
    init_db(engine)

    # 2. Nạp Taxonomy từ YAML
    aspects_yaml_path = Path(settings.configs_dir) / "aspects.yaml"
    if aspects_yaml_path.is_file():
        logger.info("Loading taxonomy from: %s", aspects_yaml_path)
        taxonomy = Taxonomy.load_from_yaml(aspects_yaml_path)
    else:
        logger.warning("Aspects YAML not found at %s. Using empty taxonomy.", aspects_yaml_path)
        taxonomy = Taxonomy([])
    app.state.taxonomy = taxonomy

    # 3. Nạp mô hình cảm xúc (lazy / mock)
    model_name = settings.model_name.lower()
    app.state.model_name = model_name
    if model_name == "baseline":
        logger.info("Initializing ZeroShotNliModel...")
        app.state.sentiment_model = ZeroShotNliModel(model_name_or_path="valhalla/distilbart-mnli-12-3")
    else:
        logger.info("Initializing MockSentimentModel for development/testing...")
        app.state.sentiment_model = MockSentimentModel()

    # 4. Khởi tạo hàng đợi In-memory Max-Heap và nạp lại từ SQLite
    queue = TicketPriorityQueue()
    with SessionLocal() as db:
        unresolved = TicketRepository.get_unresolved_tickets(db)
        for t in unresolved:
            queue.push(t.id, t.priority_score, t.created_at, t)
        logger.info("Reloaded %d unresolved tickets from SQLite into priority heap.", len(unresolved))
    app.state.priority_queue = queue

    yield

    # Cleanup nếu cần
    logger.info("Shutting down Ticket Triage application.")

app = FastAPI(
    title="Sentiment-Driven Ticket Triage API",
    description="Hệ thống phân loại và định tuyến vé hỗ trợ khách hàng theo cảm xúc",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn các routers với tiền tố chuẩn /api/v1
app.include_router(health.router, prefix="/api/v1")
app.include_router(meta.router, prefix="/api/v1")
app.include_router(tickets.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")
