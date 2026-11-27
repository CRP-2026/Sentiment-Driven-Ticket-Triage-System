from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ticket_triage.api.dependencies import get_current_admin
from ticket_triage.api.main import app
from ticket_triage.core.queue.priority_queue import TicketPriorityQueue
from ticket_triage.core.sentiment.mock import MockSentimentModel
from ticket_triage.core.taxonomy import Taxonomy
from ticket_triage.db.models import Base
from ticket_triage.domain.entities import UserEntity


@pytest.fixture
def in_memory_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def mock_model():
    return MockSentimentModel()


@pytest.fixture
def sample_taxonomy():
    yaml_path = Path(__file__).resolve().parent.parent / "configs" / "aspects.yaml"
    if yaml_path.is_file():
        return Taxonomy.load_from_yaml(yaml_path)
    return Taxonomy([])


@pytest.fixture
def priority_queue():
    return TicketPriorityQueue()


def _make_test_admin() -> UserEntity:
    return UserEntity(
        id=999,
        email="test-admin@triage.shop",
        full_name="Test Admin",
        password_hash="",
        role="admin",
        is_active=True,
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def client(in_memory_db):
    """Legacy TestClient fixture with Admin auth pre-authenticated for existing tests."""
    from ticket_triage.db.session import get_db

    engine = in_memory_db.bind
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_admin] = _make_test_admin
    app.state.testing = True
    app.state.sentiment_model = MockSentimentModel()

    yaml_path = Path(__file__).resolve().parent.parent / "configs" / "aspects.yaml"
    app.state.taxonomy = Taxonomy.load_from_yaml(yaml_path) if yaml_path.is_file() else Taxonomy([])

    with TestClient(app) as test_client:
        test_client.app.state.priority_queue = TicketPriorityQueue()
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def api_client(in_memory_db):
    """Strict TestClient fixture enforcing real JWT authentication and RBAC (no auth bypass)."""
    from ticket_triage.db.session import get_db

    engine = in_memory_db.bind
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.state.testing = True
    app.state.sentiment_model = MockSentimentModel()

    yaml_path = Path(__file__).resolve().parent.parent / "configs" / "aspects.yaml"
    app.state.taxonomy = Taxonomy.load_from_yaml(yaml_path) if yaml_path.is_file() else Taxonomy([])

    with TestClient(app) as test_client:
        test_client.app.state.priority_queue = TicketPriorityQueue()
        yield test_client

    app.dependency_overrides.clear()
