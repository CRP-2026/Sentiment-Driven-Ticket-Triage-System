from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..settings import settings

db_url = "sqlite:///:memory:" if settings.is_testing() else settings.db_url
engine_kwargs: dict[str, Any] = {"echo": False}

if db_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 15}
else:
    # Cloud PostgreSQL readiness (Neon / Supabase / Render)
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(db_url, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
