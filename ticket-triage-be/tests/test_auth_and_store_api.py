"""Integration tests for JWT Auth, Admin RBAC (401/403), Storefront & Review-to-Triage flow."""

from sqlalchemy import create_engine, text

from ticket_triage.adapters.security.pbkdf2_hasher import Pbkdf2PasswordHasher
from ticket_triage.db.init_db import init_db
from ticket_triage.db.models import Category, Product, User


def _seed_store_catalog_and_admin(db):
    hasher = Pbkdf2PasswordHasher()
    admin = User(
        email="admin@triage.shop",
        full_name="Store Admin",
        password_hash=hasher.hash_password("Admin@123"),
        role="admin",
        is_active=True,
    )
    cat_phone = Category(
        slug="smartphones",
        name="Điện thoại",
        description="Smartphone chính hãng",
        icon="smartphone",
    )
    db.add_all([admin, cat_phone])
    db.flush()

    prod = Product(
        category_id=cat_phone.id,
        slug="aerophone-pro-256",
        name="AeroPhone Pro 256GB",
        short_description="Flagship camera & long battery life",
        description="High-performance smartphone with 256GB storage and fast charging.",
        price=749.0,
        image_url="/images/products/aerophone-pro.svg",
        sku="PH-AERO-256",
        stock=15,
    )
    db.add(prod)
    db.commit()
    return admin, cat_phone, prod


def test_auth_register_login_and_admin_rbac_enforcement(api_client, in_memory_db):
    _seed_store_catalog_and_admin(in_memory_db)

    # 1. Unauthenticated requests to Admin endpoints MUST fail with 401
    assert api_client.get("/api/v1/tickets").status_code == 401
    assert api_client.get("/api/v1/stats/overview").status_code == 401
    assert api_client.get("/api/v1/stats/aspects").status_code == 401
    assert api_client.post("/api/v1/tickets", json={"content": "Refund now!"}).status_code == 401

    # 2. Public endpoints remain accessible without token
    assert api_client.get("/api/v1/health").status_code == 200
    assert api_client.get("/api/v1/meta/aspects").status_code == 200
    assert api_client.get("/api/v1/store/categories").status_code == 200
    assert api_client.get("/api/v1/store/products").status_code == 200

    # 3. Register a new customer
    reg_res = api_client.post(
        "/api/v1/auth/register",
        json={
            "email": "linh.customer@example.com",
            "full_name": "Linh Customer",
            "password": "Password123",
        },
    )
    assert reg_res.status_code == 201
    reg_body = reg_res.json()
    customer_token = reg_body["access_token"]
    assert reg_body["user"]["role"] == "customer"
    assert reg_body["user"]["created_at"].endswith("Z")

    # Duplicate email returns 409 Conflict
    dup_res = api_client.post(
        "/api/v1/auth/register",
        json={
            "email": "LINH.CUSTOMER@example.com",
            "full_name": "Duplicate",
            "password": "Password123",
        },
    )
    assert dup_res.status_code == 409

    # /auth/me returns customer profile
    me_res = api_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "linh.customer@example.com"

    # 4. Customer attempting Admin endpoints MUST fail with 403 Forbidden
    cust_headers = {"Authorization": f"Bearer {customer_token}"}
    assert api_client.get("/api/v1/tickets", headers=cust_headers).status_code == 403
    assert api_client.get("/api/v1/stats/overview", headers=cust_headers).status_code == 403
    assert api_client.post(
        "/api/v1/tickets",
        json={"content": "Should be blocked for customer role."},
        headers=cust_headers,
    ).status_code == 403

    # 5. Admin login succeeds and accesses Admin endpoints
    login_res = api_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@triage.shop", "password": "Admin@123"},
    )
    assert login_res.status_code == 200
    admin_token = login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    assert api_client.get("/api/v1/tickets", headers=admin_headers).status_code == 200
    assert api_client.get("/api/v1/stats/overview", headers=admin_headers).status_code == 200

    # Wrong password fails with 401
    bad_login = api_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@triage.shop", "password": "wrong"},
    )
    assert bad_login.status_code == 401


def test_storefront_review_dispatches_to_admin_triage_and_updates_amazon_top_aspects(
    api_client, in_memory_db
):
    _seed_store_catalog_and_admin(in_memory_db)

    # Unauthenticated review submission must be rejected (401)
    unauth = api_client.post(
        "/api/v1/store/products/aerophone-pro-256/reviews",
        json={"content": "Great phone and fast delivery!"},
    )
    assert unauth.status_code == 401

    # Register customer & login admin
    cust_token = api_client.post(
        "/api/v1/auth/register",
        json={
            "email": "buyer@example.com",
            "full_name": "Minh Buyer",
            "password": "Password123",
        },
    ).json()["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    admin_token = api_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@triage.shop", "password": "Admin@123"},
    ).json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Customer posts 2 positive reviews praising quality & shipping
    r1 = api_client.post(
        "/api/v1/store/products/aerophone-pro-256/reviews",
        json={
            "title": "Fast delivery",
            "content": "Fast shipping and excellent packaging! Very happy with this delivery.",
        },
        headers=cust_headers,
    )
    assert r1.status_code == 201
    r1_data = r1.json()
    assert r1_data["triage"]["sentiment_label"] == "positive"
    assert r1_data["triage"]["priority_level"] == "LOW"
    assert r1_data["insights"]["satisfaction_rate"] == 1.0
    assert r1_data["insights"]["top_ranked_aspects"][0]["rank"] == 1
    assert r1_data["insights"]["top_ranked_aspects"][0]["aspect_id"] == "shipping"

    r2 = api_client.post(
        "/api/v1/store/products/aerophone-pro-256/reviews",
        json={
            "title": "Solid quality",
            "content": "Awesome quality material and helpful support staff, thank you!",
        },
        headers=cust_headers,
    )
    assert r2.status_code == 201

    # 2. Customer posts an urgent billing complaint -> MUST jump to CRITICAL in Admin Triage
    r3 = api_client.post(
        "/api/v1/store/products/aerophone-pro-256/reviews",
        json={
            "title": "Double billed",
            "content": "I was charged twice for this phone! Please refund immediately or I will file a chargeback!",
        },
        headers=cust_headers,
    )
    assert r3.status_code == 201
    r3_data = r3.json()
    assert r3_data["triage"]["priority_level"] == "CRITICAL"
    assert r3_data["triage"]["priority_score"] >= 70.0
    assert r3_data["insights"]["total_reviews"] == 3
    assert r3_data["insights"]["positive_review_count"] == 2
    assert r3_data["insights"]["negative_review_count"] == 1

    # 3. Customer posts a Vietnamese comment -> triggers manual review floor 50.0
    r4 = api_client.post(
        "/api/v1/store/products/aerophone-pro-256/reviews",
        json={"content": "Điện thoại giao nhanh nhưng tôi muốn hỏi về bảo hành sản phẩm."},
        headers=cust_headers,
    )
    assert r4.status_code == 201
    assert r4.json()["triage"]["needs_manual_review"] is True
    assert r4.json()["triage"]["priority_score"] == 50.0

    # 4. Product catalog & detail expose AI satisfaction rate + Top 1-2-3 aspects (no fake stars)
    catalog_res = api_client.get("/api/v1/store/products?category=smartphones")
    assert catalog_res.status_code == 200
    catalog_item = catalog_res.json()["items"][0]
    assert catalog_item["slug"] == "aerophone-pro-256"
    assert catalog_item["total_reviews"] == 4
    assert len(catalog_item["top_ranked_aspects"]) >= 1
    assert "rating" not in catalog_item

    detail_filtered = api_client.get(
        "/api/v1/store/products/aerophone-pro-256?aspect=refund_payment"
    )
    assert detail_filtered.status_code == 200
    assert detail_filtered.json()["total_filtered_reviews"] == 1
    assert "charged twice" in detail_filtered.json()["reviews"][0]["content"]

    # 5. Admin Inbox receives all reviews ranked by priority with product provenance
    inbox_res = api_client.get("/api/v1/tickets", headers=admin_headers)
    assert inbox_res.status_code == 200
    tickets = inbox_res.json()["items"]
    assert len(tickets) == 4
    top_ticket = tickets[0]
    assert top_ticket["priority_level"] == "CRITICAL"
    assert top_ticket["source"] == "storefront_review"
    assert top_ticket["product_slug"] == "aerophone-pro-256"
    assert top_ticket["product_name"] == "AeroPhone Pro 256GB"
    assert top_ticket["author_name"] == "Minh Buyer"

    # 6. Admin image upload works via ImageStoragePort (LocalFallback in test mode)
    upload_res = api_client.post(
        "/api/v1/store/uploads/image",
        files={"file": ("demo.png", b"\x89PNG\r\n\x1a\ncontent", "image/png")},
        headers=admin_headers,
    )
    assert upload_res.status_code == 201
    assert upload_res.json()["image_url"].startswith("/images/products/")

    bad_upload = api_client.post(
        "/api/v1/store/uploads/image",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        headers=admin_headers,
    )
    assert bad_upload.status_code == 422

    svg_upload = api_client.post(
        "/api/v1/store/uploads/image",
        files={"file": ("xss.svg", b"<svg><script>alert(1)</script></svg>", "image/svg+xml")},
        headers=admin_headers,
    )
    assert svg_upload.status_code == 422


def test_storefront_works_with_remote_http_triage_without_local_tickets_rows(
    in_memory_db, sample_taxonomy
):
    """Proves bounded-context isolation: Storefront DB needs zero rows in `tickets`
    when dispatching to a remote Triage microservice via HttpTriageGateway.
    """
    import httpx

    from ticket_triage.adapters.persistence.sqlalchemy_repos import (
        SqlAlchemyCatalogRepository,
        SqlAlchemyReviewRepository,
        SqlAlchemyUserRepository,
    )
    from ticket_triage.adapters.storage.local_storage import LocalFallbackImageStorage
    from ticket_triage.adapters.triage.http_gateway import HttpTriageGateway
    from ticket_triage.application.catalog_service import CatalogService
    from ticket_triage.application.review_service import ReviewService

    _seed_store_catalog_and_admin(in_memory_db)
    user = SqlAlchemyUserRepository(in_memory_db).create(
        email="splitdb@example.com",
        full_name="Split DB Buyer",
        password_hash="h",
        role="customer",
    )

    def remote_triage_handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            201,
            json={
                "id": 9999,  # Ticket lives ONLY on remote Triage DB, NOT in Storefront DB
                "sentiment_label": "positive",
                "confidence": 0.96,
                "priority_score": 5.0,
                "priority_level": "LOW",
                "dominant_aspect": "shipping",
                "needs_manual_review": False,
                "aspects": [
                    {
                        "aspect": "shipping",
                        "sentiment": "positive",
                        "confidence": 0.96,
                        "terms": ["fast shipping"],
                    }
                ],
            },
        )

    remote_gateway = HttpTriageGateway(
        base_url="https://remote-triage.example.com",
        http_client=httpx.Client(transport=httpx.MockTransport(remote_triage_handler)),
    )
    catalog_repo = SqlAlchemyCatalogRepository(in_memory_db)
    review_repo = SqlAlchemyReviewRepository(in_memory_db)

    review_svc = ReviewService(
        catalog_repo=catalog_repo,
        review_repo=review_repo,
        triage_gateway=remote_gateway,
        taxonomy=sample_taxonomy,
    )
    res = review_svc.submit_review(
        user=user,
        product_slug="aerophone-pro-256",
        content="Super fast shipping and sturdy box!",
    )
    assert res.review.ticket_id == 9999
    assert res.insights.total_reviews == 1
    assert res.insights.top_ranked_aspects[0].aspect_id == "shipping"
    assert res.insights.top_ranked_aspects[0].rank == 1

    catalog_svc = CatalogService(
        catalog_repo=catalog_repo,
        review_repo=review_repo,
        image_storage=LocalFallbackImageStorage(),
        taxonomy=sample_taxonomy,
    )
    detail = catalog_svc.get_product_detail("aerophone-pro-256", aspect="shipping")
    assert detail.total_filtered_reviews == 1
    assert detail.insights.satisfaction_rate == 1.0


def test_init_db_upgrades_legacy_sqlite_tickets_table(tmp_path):
    legacy_db = tmp_path / "legacy.db"
    eng = create_engine(f"sqlite:///{legacy_db}", connect_args={"check_same_thread": False})
    with eng.connect() as conn:
        conn.execute(
            text(
                "CREATE TABLE tickets ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "content TEXT NOT NULL, "
                "status VARCHAR(30) DEFAULT 'new'"
                ");"
            )
        )
        conn.commit()

    init_db(eng)

    with eng.connect() as conn:
        cols = {row[1] for row in conn.execute(text("PRAGMA table_info(tickets);")).all()}
    eng.dispose()

    assert {
        "source",
        "product_id",
        "product_name",
        "product_slug",
        "user_id",
        "author_name",
    }.issubset(cols)
