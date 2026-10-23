from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from ..settings import settings

connect_args = {}
if settings.db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.db_url,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
