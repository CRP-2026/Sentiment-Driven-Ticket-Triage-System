"""M-ABSA dataset detokenizer and 2-layer product-matched seed curator.

Layer 1: Match review source domain strictly (`phone`, `laptop`, or `food` when expanded).
Layer 2: Route reviews to specific products by attribute keywords while excluding
conflicting external brand/model names, ensuring authentic Amazon-style aspect diversity.
"""

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from ...core.preprocessing.keyword_prefilter import filter_candidate_aspects
from ...core.priority.priority_engine import load_priority_rules
from ...domain.ports.seeding import (
    SeedBundle,
    SeedCategory,
    SeedProduct,
    SeedReview,
    SeedUser,
)

# Common external brand/carrier tokens filtered out so reviews match our store catalog cleanly
_CONFLICTING_BRANDS_RE = re.compile(
    r"\b(?:"
    r"samsungs?|galaxy|iphones?|ipads?|apple|macbooks?|mb\s+air|huawei|xiaomi|redmi|"
    r"oneplus|one\s+plus|nokia|motorola|moto\s+[ge]|pixel|sony|xperia|htc|lg|"
    r"dell|hp|hewlett|lenovo|thinkpad|asus|acer|toshiba|msi|surface|pavilion|"
    r"inspiron|oukitel|realme|oppo|vivo|blu|alcatel|kyocera|blackberry|zte|"
    r"walmart|ebay|best\s+buy|verizon|sprint|at&t|t-mobile|boost|metro\s*pcs|"
    r"cricket|tracfone|straight\s+talk|amazon|keurig|xs\s+max|a\d{2}|s\d{2}|"
    r"note\s*\d+|google\s+play|windows\s+\d+|mac\s*os"
    r")\b",
    re.IGNORECASE,
)

_CHROMEBOOK_TERMS_RE = re.compile(
    r"\b(?:chromebook|chromeos|chrome\s*os|flipbook)\b", re.IGNORECASE
)
_PROTECTOR_CASE_RE = re.compile(
    r"\b(?:screen\s+protector|tempered\s+glass|protector|phone\s+case)\b", re.IGNORECASE
)
_WHOLE_DEVICE_RE = re.compile(
    r"\b(?:laptop|laptops|notebook|computer|pc|screen|display|battery|phone|phones|"
    r"mobile|smartphone|camera|sim\s+card|charger|speakers?|convertible|tablet)\b",
    re.IGNORECASE,
)
_URL_OR_EMAIL_RE = re.compile(r"https?://|www\.|@", re.IGNORECASE)
_LEADING_BULLET_RE = re.compile(r"^[\s\*\-\u2022]+")

DEFAULT_SEED_USERS: tuple[SeedUser, ...] = (
    SeedUser(
        email="admin@triage.shop",
        full_name="Quản trị viên Triage",
        password="Admin@123",
        role="admin",
    ),
    SeedUser(
        email="customer@triage.shop",
        full_name="Minh Khách Hàng",
        password="Customer@123",
        role="customer",
    ),
    SeedUser(
        email="alex.chen@triage.shop",
        full_name="Alex Chen",
        password="Customer@123",
        role="customer",
    ),
    SeedUser(
        email="maya.patel@triage.shop",
        full_name="Maya Patel",
        password="Customer@123",
        role="customer",
    ),
    SeedUser(
        email="david.miller@triage.shop",
        full_name="David Miller",
        password="Customer@123",
        role="customer",
    ),
)

_CUSTOMER_AUTHOR_EMAILS: tuple[str, ...] = (
    "customer@triage.shop",
    "alex.chen@triage.shop",
    "maya.patel@triage.shop",
    "david.miller@triage.shop",
)


@dataclass(frozen=True)
class _MabsaRecord:
    text: str
    domain: str
    language: str
    polarity: str  # positive | negative | neutral
    aspects: tuple[str, ...]
    has_urgency: bool


@dataclass(frozen=True)
class _ProductSelectionRule:
    product: SeedProduct
    source_domains: tuple[str, ...]
    prefer_keywords: tuple[str, ...]
    exclude_pattern: re.Pattern[str] | None = None
    target_positive: int = 6
    target_neutral: int = 1
    target_negative: int = 3


# Data-driven catalog templates — add "food" in --domains later with zero logic changes!
CATEGORY_TEMPLATES: dict[str, SeedCategory] = {
    "smartphones": SeedCategory(
        slug="smartphones",
        name="Điện thoại",
        description="Smartphone hiệu năng cao, pin bền và camera sắc nét",
        icon="smartphone",
    ),
    "laptops": SeedCategory(
        slug="laptops",
        name="Laptop",
        description="Laptop học tập, di động mỏng nhẹ và máy trạm hiệu năng",
        icon="laptop",
    ),
    "accessories": SeedCategory(
        slug="accessories",
        name="Phụ kiện & Thiết bị",
        description="Sạc nhanh USB-C, bàn phím và thiết bị ngoại vi đồng bộ",
        icon="cpu",
    ),
    "food": SeedCategory(
        slug="food",
        name="Cà phê & Thực phẩm",
        description="Cà phê rang xay, trà và thực phẩm chọn lọc",
        icon="coffee",
    ),
}

PRODUCT_RULES: dict[str, tuple[_ProductSelectionRule, ...]] = {
    "phone": (
        _ProductSelectionRule(
            product=SeedProduct(
                category_slug="smartphones",
                slug="aerophone-pro-256",
                name="AeroPhone Pro 256GB",
                short_description="Flagship camera 50MP, bộ nhớ 256GB và cảm biến vân tay siêu nhạy.",
                description=(
                    "AeroPhone Pro 256GB kết hợp cụm camera độ phân giải cao, bộ nhớ lưu trữ lớn "
                    "và tốc độ xử lý mượt mà cho công việc lẫn giải trí cả ngày dài."
                ),
                price=749.0,
                image_url="/images/products/aerophone-pro.svg",
                sku="PH-AERO-256",
                stock=18,
            ),
            source_domains=("phone",),
            prefer_keywords=(
                "camera", "picture", "photo", "storage", "memory", "fingerprint",
                "screen", "display", "fast", "shipping", "quality",
            ),
            exclude_pattern=_PROTECTOR_CASE_RE,
            target_positive=7,
            target_neutral=1,
            target_negative=2,
        ),
        _ProductSelectionRule(
            product=SeedProduct(
                category_slug="smartphones",
                slug="nova-5g-lite",
                name="Nova 5G Lite 128GB",
                short_description="Smartphone 5G tầm trung tối ưu pin và chi phí cho nhu cầu hàng ngày.",
                description=(
                    "Nova 5G Lite nổi bật với viên pin bền bỉ, giao diện thân thiện và mức giá "
                    "hợp lý cho sinh viên và nhân viên văn phòng."
                ),
                price=379.0,
                image_url="/images/products/nova-5g-lite.svg",
                sku="PH-NOVA-128",
                stock=32,
            ),
            source_domains=("phone",),
            prefer_keywords=(
                "price", "money", "value", "battery", "delivery", "shipping",
                "service", "refund", "charge", "box", "package",
            ),
            exclude_pattern=_PROTECTOR_CASE_RE,
            target_positive=6,
            target_neutral=1,
            target_negative=3,
        ),
        _ProductSelectionRule(
            product=SeedProduct(
                category_slug="smartphones",
                slug="zenith-ultra-5g",
                name="Zenith Ultra 5G 512GB",
                short_description="Dòng flagship cao cấp khung kim loại, màn hình OLED 120Hz.",
                description=(
                    "Zenith Ultra 5G được thiết kế cho người dùng chuyên sâu với không gian lưu trữ "
                    "512GB, sạc nhanh và độ hoàn thiện chắc chắn."
                ),
                price=899.0,
                image_url="/images/products/zenith-ultra.svg",
                sku="PH-ZEN-512",
                stock=12,
            ),
            source_domains=("phone",),
            prefer_keywords=(
                "replacement", "service", "seller", "shipping", "damaged", "broken",
                "refund", "support", "quality", "fast", "delivery",
            ),
            exclude_pattern=_PROTECTOR_CASE_RE,
            target_positive=6,
            target_neutral=1,
            target_negative=3,
        ),
    ),
    "laptop": (
        _ProductSelectionRule(
            product=SeedProduct(
                category_slug="laptops",
                slug="chromeflip-book-14",
                name="ChromeFlip Book 14 2-in-1",
                short_description="Laptop gập 360 độ gọn nhẹ, khởi động nhanh cho học tập và văn phòng.",
                description=(
                    "ChromeFlip Book 14 linh hoạt chuyển đổi giữa chế độ laptop và máy tính bảng "
                    "với bản lề bền bỉ và thời lượng pin cả ngày."
                ),
                price=469.0,
                image_url="/images/products/chromeflip-14.svg",
                sku="LP-CFLIP-14",
                stock=24,
            ),
            source_domains=("laptop",),
            prefer_keywords=(
                "chromebook", "chromeos", "flipbook", "tablet", "touchscreen",
                "light", "school", "battery", "price", "sturdy",
            ),
            exclude_pattern=None,
            target_positive=7,
            target_neutral=1,
            target_negative=2,
        ),
        _ProductSelectionRule(
            product=SeedProduct(
                category_slug="laptops",
                slug="ultrabook-air-13",
                name="UltraBook Air 13",
                short_description="Laptop di động siêu mỏng 1.1kg, pin 10 giờ cho người hay di chuyển.",
                description=(
                    "UltraBook Air 13 tối ưu tính di động với khung nhôm nguyên khối, bàn phím êm "
                    "và thời lượng pin dài cho lịch trình làm việc linh hoạt."
                ),
                price=999.0,
                image_url="/images/products/ultrabook-air.svg",
                sku="LP-UAIR-13",
                stock=15,
            ),
            source_domains=("laptop",),
            prefer_keywords=(
                "travel", "portable", "light", "battery", "sturdy", "work",
                "weight", "quality", "shipping", "price",
            ),
            exclude_pattern=_CHROMEBOOK_TERMS_RE,
            target_positive=6,
            target_neutral=1,
            target_negative=3,
        ),
        _ProductSelectionRule(
            product=SeedProduct(
                category_slug="laptops",
                slug="prowork-studio-15",
                name="ProWork Studio 15",
                short_description="Máy trạm di động màn hình 15.6 inch sắc nét cho lập trình và đồ họa.",
                description=(
                    "ProWork Studio 15 trang bị cấu hình mạnh mẽ, màn hình độ phủ màu cao và "
                    "hệ thống tản nhiệt ổn định cho tác vụ nặng."
                ),
                price=1399.0,
                image_url="/images/products/prowork-studio.svg",
                sku="LP-PRO-15",
                stock=9,
            ),
            source_domains=("laptop",),
            prefer_keywords=(
                "performance", "speed", "display", "screen", "speakers", "faulty",
                "defective", "broken", "support", "refund", "service",
            ),
            exclude_pattern=_CHROMEBOOK_TERMS_RE,
            target_positive=5,
            target_neutral=1,
            target_negative=4,
        ),
    ),
    "accessories": (
        _ProductSelectionRule(
            product=SeedProduct(
                category_slug="accessories",
                slug="shieldglass-case-kit",
                name="ShieldGlass Case & Screen Protector Kit",
                short_description="Bộ ốp chống sốc và kính cường lực bảo vệ màn hình chống trầy xước.",
                description=(
                    "Bộ phụ kiện bảo vệ toàn diện gồm ốp lưng ôm sát và kính cường lực độ trong cao, "
                    "dễ dán, chống va đập và đóng gói cẩn thận khi giao hàng."
                ),
                price=29.0,
                image_url="/images/products/shieldglass-kit.svg",
                sku="AC-SHD-01",
                stock=65,
            ),
            source_domains=("phone",),
            prefer_keywords=(
                "screen protector", "tempered glass", "protector", "case", "cover",
            ),
            exclude_pattern=re.compile(
                r"\b(?:camera|battery|sim\s+card|fingerprint|network|charging|wifi)\b",
                re.IGNORECASE,
            ),
            target_positive=6,
            target_neutral=1,
            target_negative=3,
        ),
        _ProductSelectionRule(
            product=SeedProduct(
                category_slug="accessories",
                slug="tactile-pro-keyboard",
                name="Tactile Pro Keyboard & Trackpad",
                short_description="Bàn phím không dây có đèn nền và bàn di cảm ứng mượt mà độ trễ thấp.",
                description=(
                    "Tactile Pro mang lại trải nghiệm gõ êm ái, hành trình phím chuẩn xác và "
                    "trackpad đa điểm tương thích tốt với laptop và máy tính bảng."
                ),
                price=119.0,
                image_url="/images/products/tactile-keyboard.svg",
                sku="AC-KBD-PRO",
                stock=28,
            ),
            source_domains=("laptop",),
            prefer_keywords=(
                "keyboard", "trackpad", "touchpad", "keys", "typing", "backlit",
            ),
            exclude_pattern=_WHOLE_DEVICE_RE,
            target_positive=6,
            target_neutral=1,
            target_negative=3,
        ),
    ),
    "food": (
        _ProductSelectionRule(
            product=SeedProduct(
                category_slug="food",
                slug="roastcraft-arabica-blend",
                name="RoastCraft Arabica Coffee Blend",
                short_description="Cà phê Arabica rang vừa hương vị cân bằng, đóng gói bảo quản kín khí.",
                description=(
                    "Hạt cà phê Arabica tuyển chọn rang mẻ nhỏ, giữ trọn hương thơm tự nhiên "
                    "và độ tươi mới khi giao tới tay khách hàng."
                ),
                price=24.0,
                image_url="/images/products/roastcraft-coffee.svg",
                sku="FD-COF-001",
                stock=60,
            ),
            source_domains=("food",),
            prefer_keywords=("coffee", "taste", "fresh", "flavor", "package", "shipping", "quality"),
            target_positive=7,
            target_neutral=1,
            target_negative=2,
        ),
    ),
}


def detokenize_mabsa_text(raw_text: str) -> str:
    """Restore natural English punctuation and contraction spacing from SemEval/M-ABSA text."""
    text = _LEADING_BULLET_RE.sub("", (raw_text or "").strip())
    if not text:
        return ""

    # Normalize tokenized quotes and dashes
    text = text.replace("``", '"').replace("` `", '"').replace("''", '"').replace("' '", '"')
    text = re.sub(r"\busb\s*-\s*c\b", "USB-C", text, flags=re.IGNORECASE)
    text = re.sub(r"\bwi\s*-\s*fi\b", "Wi-Fi", text, flags=re.IGNORECASE)

    # Rejoin English contractions: "i ' m" -> "I'm", "did n ' t" / "doesn ' t" -> "didn't" / "doesn't"
    text = re.sub(
        r"\b([A-Za-z]+)\s*n\s*'\s*t\b",
        r"\1n't",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\b([A-Za-z]+)\s*'\s*(m|s|re|ve|ll|d)\b", r"\1'\2", text, flags=re.IGNORECASE)

    # Rejoin tokenized hyphens & inch marks ("full - size" -> "full-size", '15 "' -> '15"')
    text = re.sub(r"\b([A-Za-z]+)\s+-\s+([A-Za-z]+)\b", r"\1-\2", text)
    text = re.sub(r'(\d+(?:\.\d+)?)\s+"', r'\1"', text)

    # Fix spacing around punctuation and brackets
    text = re.sub(r"\s+([.,!?;:%])", r"\1", text)
    text = re.sub(r"([(\[$])\s+", r"\1", text)
    text = re.sub(r"\s+([)\]])", r"\1", text)
    text = re.sub(r"\s{2,}", " ", text).strip()

    # Capitalize standalone pronoun "i" and sentence start
    text = re.sub(r"\bi\b", "I", text)
    text = re.sub(r"\bi('(?:m|ve|ll|d))\b", r"I\1", text)
    if text and text[0].islower():
        text = text[0].upper() + text[1:]

    return text


def _dominant_polarity_from_triplets(triplets: list[list[str]]) -> str:
    counts = {"positive": 0, "negative": 0, "neutral": 0}
    for item in triplets:
        if len(item) == 3:
            pol = str(item[2]).strip().lower()
            if pol in ("pos", "positive"):
                counts["positive"] += 1
            elif pol in ("neg", "negative"):
                counts["negative"] += 1
            elif pol in ("neu", "neutral"):
                counts["neutral"] += 1
    if counts["negative"] > 0 and counts["negative"] >= counts["positive"]:
        return "negative"
    if counts["positive"] > 0:
        return "positive"
    return "neutral"


def _has_urgency_signal(text: str, critical_kws: list[str], high_kws: list[str]) -> bool:
    tl = text.lower()
    for kw in (*critical_kws, *high_kws):
        if kw.startswith("regex:"):
            if re.search(kw[6:].strip(), tl):
                return True
        elif re.search(rf"\b{re.escape(kw)}\b", tl):
            return True
    return False


def parse_mabsa_domain(
    mabsa_root: Path,
    domain: str,
    language: str = "en",
) -> list[_MabsaRecord]:
    """Read and clean all splits (`train`, `dev`, `test`) for a given M-ABSA domain & language."""
    domain_dir = mabsa_root / domain / language
    if not domain_dir.is_dir():
        return []

    rules = load_priority_rules()
    seen_texts: set[str] = set()
    records: list[_MabsaRecord] = []

    for split_name in ("test.txt", "dev.txt", "train.txt"):
        split_file = domain_dir / split_name
        if not split_file.is_file():
            continue
        for raw_line in split_file.read_text(encoding="utf-8").splitlines():
            if "####" not in raw_line:
                continue
            raw_text, raw_labels = raw_line.split("####", 1)
            cleaned = (
                detokenize_mabsa_text(raw_text)
                if language == "en"
                else re.sub(r"\s{2,}", " ", raw_text.strip())
            )
            if not (25 <= len(cleaned) <= 360):
                continue
            if _URL_OR_EMAIL_RE.search(cleaned):
                continue
            if _CONFLICTING_BRANDS_RE.search(cleaned):
                continue

            norm_key = cleaned.lower()
            if norm_key in seen_texts:
                continue
            seen_texts.add(norm_key)

            try:
                triplets = ast.literal_eval(raw_labels.strip())
                if not isinstance(triplets, list):
                    triplets = []
            except (SyntaxError, ValueError):
                triplets = []

            if not triplets:
                continue

            polarity = _dominant_polarity_from_triplets(triplets)
            aspects = tuple(filter_candidate_aspects(cleaned)) if language == "en" else ()
            has_urgency = (
                _has_urgency_signal(cleaned, rules.critical_keywords, rules.high_keywords)
                if language == "en"
                else False
            )

            records.append(
                _MabsaRecord(
                    text=cleaned,
                    domain=domain,
                    language=language,
                    polarity=polarity,
                    aspects=aspects,
                    has_urgency=has_urgency,
                )
            )

    return records


def _score_candidate(record: _MabsaRecord, rule: _ProductSelectionRule) -> tuple[int, int, int, int]:
    tl = record.text.lower()
    kw_hits = sum(
        1 for kw in rule.prefer_keywords if re.search(rf"\b{re.escape(kw)}\b", tl)
    )
    non_general_aspects = sum(1 for a in record.aspects if a != "general")
    urgency_rank = 1 if (record.polarity == "negative" and record.has_urgency) else 0
    # Prefer rich multi-aspect & keyword-matched reviews with clear medium length (55..220 chars)
    ideal_len = 1 if 50 <= len(record.text) <= 230 else 0
    return (urgency_rank, kw_hits, non_general_aspects, ideal_len)


def _select_for_product(
    rule: _ProductSelectionRule,
    pool_by_domain: dict[str, list[_MabsaRecord]],
    used_texts: set[str],
) -> list[_MabsaRecord]:
    candidates: list[_MabsaRecord] = []
    for dom in rule.source_domains:
        for rec in pool_by_domain.get(dom, []):
            if rec.text.lower() in used_texts:
                continue
            if rule.exclude_pattern is not None and rule.exclude_pattern.search(rec.text):
                continue
            candidates.append(rec)

    # For accessories, require at least 1 explicit accessory keyword match
    if rule.product.category_slug == "accessories":
        candidates = [
            rec
            for rec in candidates
            if any(
                re.search(rf"\b{re.escape(kw)}\b", rec.text.lower())
                for kw in rule.prefer_keywords
            )
        ]

    selected: list[_MabsaRecord] = []
    quotas = (
        ("negative", rule.target_negative),
        ("positive", rule.target_positive),
        ("neutral", rule.target_neutral),
    )

    for target_pol, count in quotas:
        pol_cands = [r for r in candidates if r.polarity == target_pol]
        pol_cands.sort(key=lambda r: _score_candidate(r, rule), reverse=True)
        for rec in pol_cands:
            if len([s for s in selected if s.polarity == target_pol]) >= count:
                break
            key = rec.text.lower()
            if key in used_texts:
                continue
            used_texts.add(key)
            selected.append(rec)

    return selected


def _pick_vietnamese_samples(mabsa_root: Path, count: int = 2) -> list[_MabsaRecord]:
    vi_records = parse_mabsa_domain(mabsa_root, "phone", language="vi")
    clean_vi = [
        r
        for r in vi_records
        if 45 <= len(r.text) <= 170
        and any(ord(c) >= 128 for c in r.text)
        and "bong bóng" not in r.text.lower()
        and "nụ thật" not in r.text.lower()
    ]
    # Pick 1 clear negative + 1 clear positive Vietnamese review
    negs = [r for r in clean_vi if r.polarity == "negative"]
    poss = [r for r in clean_vi if r.polarity == "positive"]
    picked: list[_MabsaRecord] = []
    if negs:
        picked.append(negs[0])
    if poss and len(picked) < count:
        picked.append(poss[0])
    for r in clean_vi:
        if len(picked) >= count:
            break
        if r not in picked:
            picked.append(r)
    return picked[:count]


def build_curated_seed_bundle(
    mabsa_root: Path,
    domains: tuple[str, ...] = ("phone", "laptop"),
    include_accessories: bool = True,
    include_vi_samples: bool = True,
) -> SeedBundle:
    """Build a balanced, product-matched SeedBundle from M-ABSA domain text files."""
    normalized_domains = tuple(d.strip().lower() for d in domains if d.strip())
    pool_by_domain: dict[str, list[_MabsaRecord]] = {
        dom: parse_mabsa_domain(mabsa_root, dom, language="en")
        for dom in normalized_domains
    }

    active_rule_groups: list[str] = list(normalized_domains)
    if include_accessories and any(d in normalized_domains for d in ("phone", "laptop")):
        active_rule_groups.append("accessories")

    selected_rules: list[_ProductSelectionRule] = []
    for group in active_rule_groups:
        selected_rules.extend(PRODUCT_RULES.get(group, ()))

    # Select accessories FIRST so peripheral-specific reviews (keyboard/trackpad/usb-c)
    # don't get consumed by generic laptops before accessories pick them
    ordered_for_picking = sorted(
        selected_rules,
        key=lambda r: 0 if r.product.category_slug == "accessories" else 1,
    )

    used_texts: set[str] = set()
    reviews_by_product: dict[str, list[_MabsaRecord]] = {}
    for rule in ordered_for_picking:
        reviews_by_product[rule.product.slug] = _select_for_product(
            rule=rule,
            pool_by_domain=pool_by_domain,
            used_texts=used_texts,
        )

    # Attach 2 authentic Vietnamese reviews from M-ABSA phone/vi to test manual review flow
    if include_vi_samples and "phone" in normalized_domains:
        vi_samples = _pick_vietnamese_samples(mabsa_root, count=2)
        phone_slugs = [r.product.slug for r in PRODUCT_RULES.get("phone", ())]
        for idx, vi_rec in enumerate(vi_samples):
            if idx < len(phone_slugs):
                reviews_by_product.setdefault(phone_slugs[idx], []).append(vi_rec)

    # Assemble categories, products, and reviews in deterministic order
    seen_cats: list[SeedCategory] = []
    seen_cat_slugs: set[str] = set()
    products: list[SeedProduct] = []
    reviews: list[SeedReview] = []
    author_idx = 0

    for rule in selected_rules:
        cat_slug = rule.product.category_slug
        if cat_slug not in seen_cat_slugs and cat_slug in CATEGORY_TEMPLATES:
            seen_cat_slugs.add(cat_slug)
            seen_cats.append(CATEGORY_TEMPLATES[cat_slug])
        products.append(rule.product)

        for rec in reviews_by_product.get(rule.product.slug, []):
            author_email = _CUSTOMER_AUTHOR_EMAILS[author_idx % len(_CUSTOMER_AUTHOR_EMAILS)]
            author_idx += 1
            reviews.append(
                SeedReview(
                    product_slug=rule.product.slug,
                    author_email=author_email,
                    content=rec.text,
                    title=None,
                    source_domain=rec.domain,
                    source_language=rec.language,
                )
            )

    return SeedBundle(
        users=DEFAULT_SEED_USERS,
        categories=tuple(seen_cats),
        products=tuple(products),
        reviews=tuple(reviews),
    )
