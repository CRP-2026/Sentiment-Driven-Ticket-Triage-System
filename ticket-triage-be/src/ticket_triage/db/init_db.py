from sqlalchemy import Engine, text

from .models import Base

_SQLITE_TICKET_EXTRA_COLUMNS: tuple[tuple[str, str], ...] = (
    ("source", "VARCHAR(30) DEFAULT 'direct_api'"),
    ("product_id", "INTEGER"),
    ("product_name", "VARCHAR(180)"),
    ("product_slug", "VARCHAR(120)"),
    ("user_id", "INTEGER"),
    ("author_name", "VARCHAR(120)"),
)


def _ensure_sqlite_ticket_columns(engine_instance: Engine) -> None:
    """Idempotently add nullable storefront provenance columns to legacy SQLite databases."""
    with engine_instance.connect() as conn:
        rows = conn.execute(text("PRAGMA table_info(tickets);")).all()
        if not rows:
            return
        existing_cols = {row[1] for row in rows}
        altered = False
        for col_name, col_def in _SQLITE_TICKET_EXTRA_COLUMNS:
            if col_name not in existing_cols:
                conn.execute(text(f"ALTER TABLE tickets ADD COLUMN {col_name} {col_def};"))
                altered = True
        if altered:
            conn.commit()


def init_db(engine_instance: Engine) -> None:
    """Tự động kích hoạt WAL mode (nếu là SQLite), tạo toàn bộ bảng và đồng bộ cột mới."""
    url_str = str(engine_instance.url)
    is_sqlite = "sqlite" in url_str

    if is_sqlite:
        with engine_instance.connect() as conn:
            if ":memory:" not in url_str:
                current_mode = conn.execute(text("PRAGMA journal_mode;")).scalar()
                if str(current_mode).lower() != "wal":
                    conn.execute(text("PRAGMA journal_mode=WAL;"))
            conn.execute(text("PRAGMA foreign_keys=ON;"))
            conn.commit()

    Base.metadata.create_all(bind=engine_instance)

    if is_sqlite:
        _ensure_sqlite_ticket_columns(engine_instance)
