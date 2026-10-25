import re

ASPECT_KEYWORDS: dict[str, list[str]] = {
    "customer_service": [
        "agent", "representative", "support", "service", "rep", "staff",
        "attitude", "rude", "unhelpful", "reply", "response", "ticket",
        "chat", "call", "contact", "email", "manager", "assistance"
    ],
    "refund_payment": [
        "refund", "charge", "charged", "overcharged", "double charged",
        "payment", "pay", "bill", "billing", "invoice", "fee", "money back",
        "dispute", "chargeback", "credit card", "bank", "transaction", "reimburse"
    ],
    "product_quality": [
        "broken", "damaged", "defect", "defective", "cheap", "poor quality",
        "quality", "fake", "counterfeit", "faulty", "flaw", "torn", "rip",
        "stopped working", "not working", "durability", "material", "smell",
        "zipper", "button", "size", "fit", "color"
    ],
    "shipping": [
        "ship", "shipping", "deliver", "delivery", "delivered", "package",
        "parcel", "box", "tracking", "track", "transit", "carrier", "courier",
        "usps", "fedex", "ups", "late", "delay", "delayed", "never arrived",
        "lost package", "wrong address", "customs"
    ],
    "general": [
        "account", "login", "password", "website", "app", "policy", "faq",
        "question", "inquiry", "how to", "terms", "subscribe", "cancel account"
    ],
}

def filter_candidate_aspects(text: str) -> list[str]:
    """Quét tín hiệu từ khóa khía cạnh trước khi chạy NLI:
    - Trả về danh sách aspect IDs có từ khóa xuất hiện.
    - Nếu không phát hiện từ khóa cụ thể nào, mặc định trả về ['general'].
    """
    if not text:
        return ["general"]

    text_lower = text.lower()
    matched_aspects = []

    for aspect_id, keywords in ASPECT_KEYWORDS.items():
        if aspect_id == "general":
            continue

        for kw in keywords:
            # Ranh giới từ chính xác
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, text_lower):
                matched_aspects.append(aspect_id)
                break

    # Nếu không khớp nhóm nào, trả về general
    if not matched_aspects:
        return ["general"]

    return matched_aspects
