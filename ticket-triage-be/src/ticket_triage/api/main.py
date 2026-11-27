import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..adapters.persistence.sqlalchemy_repos import (
    SqlAlchemyTicketRepository,
    SqlAlchemyUserRepository,
)
from ..adapters.seeding.json_seed_source import JsonSeedSource
from ..adapters.seeding.sqlalchemy_seed_repo import SqlAlchemySeedRepository
from ..application.seed_service import SeedService
from ..application.triage_service import ticket_queue_metadata
from ..core.preprocessing.keyword_prefilter import load_aspect_keywords
from ..core.priority.priority_engine import load_priority_rules
from ..core.queue.priority_queue import TicketPriorityQueue
from ..core.sentiment.baseline import (
    DEFAULT_HF_MODELS,
    ZeroShotNliModel,
    load_aspect_hypotheses,
)
from ..core.sentiment.mock import MockSentimentModel
from ..core.taxonomy import Taxonomy
from ..db.init_db import init_db
from ..db.session import SessionLocal, engine
from ..settings import BASE_DIR, settings
from .container import AppContainer
from .error_handlers import register_error_handlers
from .routers import auth, health, meta, stats, store, tickets

logger = logging.getLogger("ticket_triage")
logging.basicConfig(level=logging.INFO)


def _is_valid_local_model_dir(path: Path) -> bool:
    """Kiểm tra thư mục local có chứa model HuggingFace hợp lệ (có config.json) hay không."""
    return path.is_dir() and (path / "config.json").is_file()


def _resolve_nli_model_source(
    model_name: str,
    model_path: str | None,
    model_id: str | None,
) -> tuple[str, str]:
    """Xác định nguồn nạp model NLI từ cấu hình .env:
    1. Thư mục local chứa config.json tại MODEL_PATH.
    2. Repo ID tường minh tại MODEL_ID trong .env.
    3. Repo HuggingFace mặc định ứng với MODEL_NAME (baseline / deberta).
    """
    cleaned_path = (model_path or "").strip()
    if cleaned_path:
        raw_path = Path(cleaned_path)
        candidate = (
            raw_path if (raw_path.is_absolute() or raw_path.exists()) else (BASE_DIR / raw_path)
        )
        if _is_valid_local_model_dir(candidate):
            return str(candidate), "local"

    cleaned_id = (model_id or "").strip()
    if cleaned_id:
        return cleaned_id, "env_model_id"

    return DEFAULT_HF_MODELS.get(model_name, DEFAULT_HF_MODELS["baseline"]), "default_hf"


@asynccontextmanager
async def lifespan(app: FastAPI):
    is_testing = getattr(app.state, "testing", False) or settings.is_testing()

    # 1. Khởi tạo CSDL (bật WAL mode nếu là SQLite, tạo bảng) nếu không phải môi trường test
    if not is_testing:
        logger.info("Initializing database...")
        init_db(engine)
    else:
        logger.info("Running in test mode: Skipping disk database initialization in lifespan.")

    # 2. Nạp Taxonomy và danh mục từ khóa lọc từ configs/aspects.yaml
    aspects_yaml_path = Path(settings.configs_dir) / "aspects.yaml"
    taxonomy = (
        Taxonomy.load_from_yaml(aspects_yaml_path) if aspects_yaml_path.is_file() else Taxonomy([])
    )
    app.state.taxonomy = taxonomy
    load_aspect_keywords.cache_clear()
    app.state.aspect_keywords = (
        load_aspect_keywords(aspects_yaml_path)
        if aspects_yaml_path.is_file()
        else load_aspect_keywords()
    )

    # 3. Nạp configs/aspect_hypotheses.yaml
    hypotheses_yaml_path = Path(settings.configs_dir) / "aspect_hypotheses.yaml"
    hypotheses_data = load_aspect_hypotheses(hypotheses_yaml_path)

    # 3b. Nạp configs/priority_rules.yaml (Single Source of Truth cho Priority Engine)
    rules_yaml_path = Path(settings.configs_dir) / "priority_rules.yaml"
    load_priority_rules.cache_clear()
    priority_rules_loaded = rules_yaml_path.is_file()
    app.state.priority_rules = (
        load_priority_rules(rules_yaml_path)
        if priority_rules_loaded
        else load_priority_rules()
    )
    logger.info("priority_rules.yaml loaded: %s", priority_rules_loaded)

    # 4. Nạp mô hình cảm xúc (lazy / mock) từ cấu hình .env
    os.environ["HF_HUB_OFFLINE"] = "1" if settings.hf_hub_offline else "0"
    model_name = settings.model_name.strip().lower() or "mock"
    raw_task = settings.model_task.strip().lower() or "absa"
    if raw_task not in ("absa", "document"):
        logger.warning("Unknown MODEL_TASK='%s'; defaulting to 'absa'.", raw_task)
        model_task = "absa"
    else:
        model_task = raw_task

    app.state.model_name = model_name
    app.state.model_task = model_task
    app.state.enable_abte = bool(settings.enable_abte)
    if model_name == "mock":
        app.state.sentiment_model = MockSentimentModel()
    else:
        resolved_source, source_kind = _resolve_nli_model_source(
            model_name=model_name,
            model_path=settings.model_path,
            model_id=settings.model_id,
        )
        if model_name in DEFAULT_HF_MODELS or source_kind in ("local", "env_model_id"):
            app.state.sentiment_model = ZeroShotNliModel(
                model_name_or_path=resolved_source,
                hypotheses=hypotheses_data,
            )
            logger.info("NLI model source: %s (kind=%s)", resolved_source, source_kind)
        else:
            logger.warning(
                "Unknown MODEL_NAME='%s' without MODEL_ID or local config.json; falling back to MockSentimentModel.",
                model_name,
            )
            app.state.sentiment_model = MockSentimentModel()

    # 4b. Khởi tạo Composition Root (SOLID-D Container)
    app.state.container = AppContainer.from_settings(settings)

    aspects_loaded = aspects_yaml_path.is_file() and len(taxonomy.get_all()) > 0
    hypotheses_loaded = hypotheses_yaml_path.is_file() and bool(hypotheses_data)

    logger.info("Model Name: %s", model_name)
    logger.info("Model Task: %s", model_task)
    logger.info("ENABLE_ABTE: %s", app.state.enable_abte)
    logger.info("aspects.yaml loaded: %s", aspects_loaded)
    logger.info("aspect_hypotheses.yaml loaded: %s", hypotheses_loaded)

    # 4c. Tùy chọn tự nạp dữ liệu Storefront & M-ABSA mẫu khi deploy DB trống (AUTO_SEED_DEMO=true)
    if not is_testing and settings.auto_seed_demo:
        default_seed_json = BASE_DIR / "seeds" / "mabsa_store_seed.json"
        if default_seed_json.is_file():
            with SessionLocal() as db:
                seed_svc = SeedService(
                    seed_source=JsonSeedSource(default_seed_json),
                    seed_repo=SqlAlchemySeedRepository(db),
                    user_repo=SqlAlchemyUserRepository(db),
                    password_hasher=app.state.container.password_hasher,
                    review_service=app.state.container.build_review_service(db, app.state),
                )
                summary = seed_svc.run(only_if_empty=True)
                if summary.products_created > 0 or summary.reviews_created > 0:
                    logger.info(
                        "AUTO_SEED_DEMO populated %d categories, %d products, %d reviews.",
                        summary.categories_created,
                        summary.products_created,
                        summary.reviews_created,
                    )

    # 5. Khởi tạo hàng đợi In-memory Max-Heap
    if not is_testing:
        queue = TicketPriorityQueue()
        with SessionLocal() as db:
            unresolved = SqlAlchemyTicketRepository(db).get_unresolved_tickets()
            for t in unresolved:
                queue.push(
                    t.id, t.priority_score, t.created_at, ticket_queue_metadata(t)
                )
            logger.info(
                "Reloaded %d unresolved tickets from database into priority heap.",
                len(unresolved),
            )
        app.state.priority_queue = queue
    else:
        if not hasattr(app.state, "priority_queue") or app.state.priority_queue is None:
            app.state.priority_queue = TicketPriorityQueue()

    yield

    logger.info("Shutting down Ticket Triage application.")


app = FastAPI(
    title="Sentiment-Driven Ticket Triage & Storefront API",
    description=(
        "Hệ thống thương mại điện tử tích hợp phân tích cảm xúc theo khía cạnh (ABSA) "
        "và phân loại ưu tiên vé hỗ trợ khách hàng"
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
)

register_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(meta.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(store.router, prefix="/api/v1")
app.include_router(tickets.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")
