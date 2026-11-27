"""JSON fixture implementation of SeedSourcePort (deploy-independent)."""

import json
from dataclasses import asdict
from pathlib import Path

from ...domain.ports.seeding import (
    SeedBundle,
    SeedCategory,
    SeedProduct,
    SeedReview,
    SeedUser,
)


def save_seed_bundle_json(bundle: SeedBundle, output_path: Path) -> None:
    """Serialize a SeedBundle into a compact UTF-8 JSON fixture."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "users": [asdict(u) for u in bundle.users],
        "categories": [asdict(c) for c in bundle.categories],
        "products": [asdict(p) for p in bundle.products],
        "reviews": [asdict(r) for r in bundle.reviews],
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


class JsonSeedSource:
    """Loads curated storefront seed data from a tracked JSON file (zero M-ABSA runtime coupling)."""

    def __init__(self, json_path: Path) -> None:
        self._json_path = json_path

    def load(self) -> SeedBundle:
        if not self._json_path.is_file():
            raise FileNotFoundError(f"Seed fixture not found at: {self._json_path}")

        data = json.loads(self._json_path.read_text(encoding="utf-8"))
        return SeedBundle(
            users=tuple(
                SeedUser(
                    email=str(u["email"]),
                    full_name=str(u["full_name"]),
                    password=str(u["password"]),
                    role="admin" if u.get("role") == "admin" else "customer",
                )
                for u in data.get("users", [])
            ),
            categories=tuple(
                SeedCategory(
                    slug=str(c["slug"]),
                    name=str(c["name"]),
                    description=str(c.get("description", "")),
                    icon=str(c.get("icon", "package")),
                )
                for c in data.get("categories", [])
            ),
            products=tuple(
                SeedProduct(
                    category_slug=str(p["category_slug"]),
                    slug=str(p["slug"]),
                    name=str(p["name"]),
                    short_description=str(p.get("short_description", "")),
                    description=str(p.get("description", "")),
                    price=float(p["price"]),
                    image_url=str(p.get("image_url", "")),
                    sku=str(p["sku"]),
                    stock=int(p.get("stock", 25)),
                )
                for p in data.get("products", [])
            ),
            reviews=tuple(
                SeedReview(
                    product_slug=str(r["product_slug"]),
                    author_email=str(r["author_email"]),
                    content=str(r["content"]),
                    title=r.get("title"),
                    source_domain=str(r.get("source_domain", "mabsa")),
                    source_language=str(r.get("source_language", "en")),
                )
                for r in data.get("reviews", [])
            ),
        )
