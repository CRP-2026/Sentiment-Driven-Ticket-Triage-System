"""Tests for M-ABSA detokenizer, curated JSON fixture, and idempotent DIP SeedService."""

import re
from pathlib import Path

from ticket_triage.adapters.persistence.sqlalchemy_repos import (
    SqlAlchemyCatalogRepository,
    SqlAlchemyReviewRepository,
    SqlAlchemyTicketRepository,
    SqlAlchemyUserRepository,
)
from ticket_triage.adapters.security.pbkdf2_hasher import Pbkdf2PasswordHasher
from ticket_triage.adapters.seeding.json_seed_source import JsonSeedSource
from ticket_triage.adapters.seeding.mabsa_parser import detokenize_mabsa_text
from ticket_triage.adapters.seeding.sqlalchemy_seed_repo import SqlAlchemySeedRepository
from ticket_triage.adapters.triage.local_gateway import LocalTriageGateway
from ticket_triage.application.review_service import ReviewService
from ticket_triage.application.seed_service import SeedService
from ticket_triage.application.triage_service import TriageService
from ticket_triage.core.sentiment.mock import MockSentimentModel
from ticket_triage.domain.ports.seeding import SeedRepositoryPort, SeedSourcePort

SEED_JSON_PATH = Path(__file__).resolve().parent.parent / "seeds" / "mabsa_store_seed.json"


def test_detokenize_mabsa_text_fixes_contractions_hyphens_and_punctuation():
    assert detokenize_mabsa_text("i ' m very happy with this usb - c cable .") == (
        "I'm very happy with this USB-C cable."
    )
    assert detokenize_mabsa_text("it did n ' t turn on , and it doesn ' t charge !") == (
        "It didn't turn on, and it doesn't charge!"
    )
    assert detokenize_mabsa_text('15 " screen with full - size keyboard ( great ) .') == (
        '15" screen with full-size keyboard (great).'
    )


def test_curated_mabsa_seed_fixture_integrity_and_no_brand_leaks():
    source = JsonSeedSource(SEED_JSON_PATH)
    assert isinstance(source, SeedSourcePort)

    bundle = source.load()
    assert len(bundle.users) >= 2
    assert {u.email for u in bundle.users} >= {"admin@triage.shop", "customer@triage.shop"}
    assert [c.slug for c in bundle.categories] == ["smartphones", "laptops", "accessories"]
    assert len(bundle.products) == 8
    assert len(bundle.reviews) >= 80

    langs = {r.source_language for r in bundle.reviews}
    assert langs == {"en", "vi"}

    # Ensure every product received reviews and no conflicting brands leaked into fixture
    product_slugs = {p.slug for p in bundle.products}
    covered_slugs = {r.product_slug for r in bundle.reviews}
    assert covered_slugs == product_slugs

    forbidden_brands = re.compile(
        r"\b(?:samsungs?|iphones?|macbooks?|lenovo|dell|asus)\b", re.IGNORECASE
    )
    for rev in bundle.reviews:
        assert not forbidden_brands.search(rev.content), f"Brand leak in: {rev.content}"
        assert "doesn ' t" not in rev.content
        assert "did n ' t" not in rev.content


def test_seed_service_is_idempotent_and_powers_storefront_and_admin_triage(
    api_client, in_memory_db, sample_taxonomy
):
    seed_repo = SqlAlchemySeedRepository(in_memory_db)
    assert isinstance(seed_repo, SeedRepositoryPort)

    triage_svc = TriageService(
        ticket_repo=SqlAlchemyTicketRepository(in_memory_db),
        sentiment_model=MockSentimentModel(),
        priority_queue=api_client.app.state.priority_queue,
        taxonomy=sample_taxonomy,
        enable_abte=True,
    )
    review_svc = ReviewService(
        catalog_repo=SqlAlchemyCatalogRepository(in_memory_db),
        review_repo=SqlAlchemyReviewRepository(in_memory_db),
        triage_gateway=LocalTriageGateway(triage_svc),
        taxonomy=sample_taxonomy,
    )
    seed_svc = SeedService(
        seed_source=JsonSeedSource(SEED_JSON_PATH),
        seed_repo=seed_repo,
        user_repo=SqlAlchemyUserRepository(in_memory_db),
        password_hasher=Pbkdf2PasswordHasher(iterations=10_000),
        review_service=review_svc,
    )

    # First run populates everything cleanly
    first = seed_svc.run(only_if_empty=False)
    assert first.categories_created == 3
    assert first.products_created == 8
    assert first.reviews_created >= 80
    assert first.reviews_skipped == 0

    # Second run MUST be 100% idempotent (zero duplicates!)
    second = seed_svc.run(only_if_empty=False)
    assert second.users_created == 0
    assert second.categories_created == 0
    assert second.products_created == 0
    assert second.reviews_created == 0
    assert second.reviews_skipped == first.reviews_created

    # Storefront API serves categories + products with AI satisfaction & Top 1-2-3 (Option A)
    cats_res = api_client.get("/api/v1/store/categories")
    assert cats_res.status_code == 200
    assert len(cats_res.json()) == 3

    prods_res = api_client.get("/api/v1/store/products")
    assert prods_res.status_code == 200
    prod_items = prods_res.json()["items"]
    assert len(prod_items) == 8
    assert all(item["total_reviews"] >= 10 for item in prod_items)
    assert any(
        len(item["top_ranked_aspects"]) >= 1 and item["top_ranked_aspects"][0]["rank"] == 1
        for item in prod_items
    )

    # Seeded Admin logs in and sees all reviews triaged across CRITICAL / MEDIUM / LOW
    admin_login = api_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@triage.shop", "password": "Admin@123"},
    )
    assert admin_login.status_code == 200
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

    stats_res = api_client.get("/api/v1/stats/overview", headers=admin_headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_tickets"] == first.reviews_created
    assert stats["priority_counts"].get("CRITICAL", 0) >= 1
    assert stats["priority_counts"].get("MEDIUM", 0) >= 1
    assert stats["priority_counts"].get("LOW", 0) >= 1

    # Seeded Customer logs in cleanly with customer role
    cust_login = api_client.post(
        "/api/v1/auth/login",
        json={"email": "customer@triage.shop", "password": "Customer@123"},
    )
    assert cust_login.status_code == 200
    assert cust_login.json()["user"]["role"] == "customer"
