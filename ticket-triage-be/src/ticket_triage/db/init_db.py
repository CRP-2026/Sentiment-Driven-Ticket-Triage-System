from sqlalchemy import Engine, text
from .models import Base

def init_db(engine_instance: Engine) -> None:
    """Tự động kích hoạt WAL mode (nếu là SQLite) và tạo toàn bộ bảng."""
    url_str = str(engine_instance.url)
    if "sqlite" in url_str:
        with engine_instance.connect() as conn:
            # WAL mode chỉ áp dụng cho SQLite file, không dùng cho in-memory
            if ":memory:" not in url_str:
                conn.execute(text("PRAGMA journal_mode=WAL;"))
            conn.execute(text("PRAGMA foreign_keys=ON;"))
            conn.commit()

    Base.metadata.create_all(bind=engine_instance)
