"""Build compact deploy-ready JSON seed fixture from data/GiuaKiAI/M-ABSA/data.

Usage:
    python scripts/build_seed_from_mabsa.py
    python scripts/build_seed_from_mabsa.py --domains phone laptop food
"""

import argparse
import collections
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

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR / "src"))

from ticket_triage.adapters.seeding.json_seed_source import save_seed_bundle_json
from ticket_triage.adapters.seeding.mabsa_parser import build_curated_seed_bundle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract curated, product-matched storefront reviews from M-ABSA datasets."
    )
    parser.add_argument(
        "--mabsa-dir",
        type=Path,
        default=REPO_ROOT / "data" / "GiuaKiAI" / "M-ABSA" / "data",
        help="Path to M-ABSA data directory containing <domain>/<lang>/*.txt",
    )
    parser.add_argument(
        "--domains",
        nargs="+",
        default=["phone", "laptop"],
        help="M-ABSA domains to include (e.g. phone laptop, expandable to food).",
    )
    parser.add_argument(
        "--no-accessories",
        action="store_true",
        help="Disable derived accessories category.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BACKEND_DIR / "seeds" / "mabsa_store_seed.json",
        help="Destination path for compact deploy-ready JSON fixture.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.mabsa_dir.is_dir():
        raise SystemExit(f"M-ABSA data directory not found: {args.mabsa_dir}")

    bundle = build_curated_seed_bundle(
        mabsa_root=args.mabsa_dir,
        domains=tuple(args.domains),
        include_accessories=not args.no_accessories,
        include_vi_samples=True,
    )
    save_seed_bundle_json(bundle, args.output)

    by_product = collections.Counter(r.product_slug for r in bundle.reviews)
    by_lang = collections.Counter(r.source_language for r in bundle.reviews)
    print(f"Wrote seed fixture -> {args.output} ({args.output.stat().st_size:,} bytes)")
    print(
        f"Summary: {len(bundle.users)} users | {len(bundle.categories)} categories | "
        f"{len(bundle.products)} products | {len(bundle.reviews)} real M-ABSA reviews"
    )
    print(f"Languages: {dict(by_lang)}")
    for prod in bundle.products:
        print(f"  - {prod.slug:24s} ({prod.category_slug:11s}): {by_product[prod.slug]} reviews")


if __name__ == "__main__":
    main()
