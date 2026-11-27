"""Idempotent CLI seeder loading curated real M-ABSA storefront reviews via DIP SeedService.

Usage:
    python scripts/seed_demo_data.py
    python scripts/seed_demo_data.py --seed-file seeds/mabsa_store_seed.json
    python scripts/seed_demo_data.py --mabsa-dir ../data/GiuaKiAI/M-ABSA/data --domains phone laptop
"""

import argparse
import io
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, io.UnsupportedOperation):
        pass

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
sys.path.insert(0, str(BACKEND_DIR / "src"))

from ticket_triage.adapters.persistence.sqlalchemy_repos import (
    SqlAlchemyCatalogRepository,
    SqlAlchemyReviewRepository,
    SqlAlchemyTicketRepository,
    SqlAlchemyUserRepository,
)
from ticket_triage.adapters.security.pbkdf2_hasher import Pbkdf2PasswordHasher
from ticket_triage.adapters.seeding.json_seed_source import JsonSeedSource
from ticket_triage.adapters.seeding.mabsa_seed_source import MabsaDirectorySeedSource
from ticket_triage.adapters.seeding.sqlalchemy_seed_repo import SqlAlchemySeedRepository
from ticket_triage.adapters.triage.local_gateway import LocalTriageGateway
from ticket_triage.application.review_service import ReviewService
from ticket_triage.application.seed_service import SeedService
from ticket_triage.application.triage_service import TriageService
from ticket_triage.core.preprocessing.keyword_prefilter import load_aspect_keywords
from ticket_triage.core.priority.priority_engine import load_priority_rules
from ticket_triage.core.sentiment.mock import MockSentimentModel
from ticket_triage.core.taxonomy import Taxonomy
from ticket_triage.db.init_db import init_db
from ticket_triage.db.session import SessionLocal, engine
from ticket_triage.domain.ports.seeding import SeedSourcePort


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Idempotently seed storefront catalog, demo accounts, and M-ABSA reviews."
    )
    parser.add_argument(
        "--seed-file",
        type=Path,
        default=BACKEND_DIR / "seeds" / "mabsa_store_seed.json",
        help="Path to curated JSON seed fixture (default: seeds/mabsa_store_seed.json).",
    )
    parser.add_argument(
        "--mabsa-dir",
        type=Path,
        default=None,
        help="Optional path to raw M-ABSA data folder to seed directly instead of JSON fixture.",
    )
    parser.add_argument(
        "--domains",
        nargs="+",
        default=["phone", "laptop"],
        help="Domains used when --mabsa-dir is provided (e.g. phone laptop food).",
    )
    return parser.parse_args()


def seed(
    seed_file: Path | None = None,
    mabsa_dir: Path | None = None,
    domains: tuple[str, ...] = ("phone", "laptop"),
) -> None:
    print("Initializing database...")
    init_db(engine)

    configs_dir = BACKEND_DIR / "configs"
    aspects_yaml = configs_dir / "aspects.yaml"
    rules_yaml = configs_dir / "priority_rules.yaml"
    taxonomy = Taxonomy.load_from_yaml(aspects_yaml) if aspects_yaml.is_file() else Taxonomy([])
    aspect_keywords = load_aspect_keywords(aspects_yaml) if aspects_yaml.is_file() else None
    priority_rules = load_priority_rules(rules_yaml) if rules_yaml.is_file() else None

    if mabsa_dir is not None:
        source: SeedSourcePort = MabsaDirectorySeedSource(
            mabsa_root=mabsa_dir,
            domains=domains,
        )
        print(f"Seed source: M-ABSA directory ({mabsa_dir}) domains={domains}")
    else:
        target_json = seed_file or (BACKEND_DIR / "seeds" / "mabsa_store_seed.json")
        source = JsonSeedSource(target_json)
        print(f"Seed source: JSON fixture ({target_json})")

    model = MockSentimentModel()
    hasher = Pbkdf2PasswordHasher()

    with SessionLocal() as db:
        triage_service = TriageService(
            ticket_repo=SqlAlchemyTicketRepository(db),
            sentiment_model=model,
            priority_queue=None,
            taxonomy=taxonomy,
            priority_rules=priority_rules,
            aspect_keywords=aspect_keywords,
            enable_abte=True,
        )
        review_service = ReviewService(
            catalog_repo=SqlAlchemyCatalogRepository(db),
            review_repo=SqlAlchemyReviewRepository(db),
            triage_gateway=LocalTriageGateway(triage_service),
            taxonomy=taxonomy,
        )
        seed_service = SeedService(
            seed_source=source,
            seed_repo=SqlAlchemySeedRepository(db),
            user_repo=SqlAlchemyUserRepository(db),
            password_hasher=hasher,
            review_service=review_service,
        )
        summary = seed_service.run(only_if_empty=False)

    print(
        "Seeding completed! "
        f"Users +{summary.users_created} | Categories +{summary.categories_created} | "
        f"Products +{summary.products_created} | Reviews +{summary.reviews_created} "
        f"(skipped existing: {summary.reviews_skipped})"
    )
    print("Demo accounts:")
    print("  - Admin:    admin@triage.shop / Admin@123")
    print("  - Customer: customer@triage.shop / Customer@123")


if __name__ == "__main__":
    cli_args = parse_args()
    seed(
        seed_file=cli_args.seed_file,
        mabsa_dir=cli_args.mabsa_dir,
        domains=tuple(cli_args.domains),
    )
