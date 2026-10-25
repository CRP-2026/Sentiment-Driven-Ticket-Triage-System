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

# Add src to path
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir / "src"))

from ticket_triage.api.services.pipeline import process_ticket_pipeline
from ticket_triage.core.sentiment.mock import MockSentimentModel
from ticket_triage.core.taxonomy import Taxonomy
from ticket_triage.db.init_db import init_db
from ticket_triage.db.session import SessionLocal, engine

DEMO_TICKETS = [
    "I was charged twice for order #9821. Please refund immediately or I will dispute the chargeback with my bank!",
    "My package is 10 days late and the tracking number is completely broken. This is ridiculous!!!",
    "I want to sue your company for delivering a fake product. Lawyer is already contacted. This is fraud!",
    "The zipper on this jacket broke on the very first day. Poor material quality, I want an exchange or refund.",
    "Customer service rep was extremely rude on phone and hung up on me while I was asking about my invoice.",
    "Could you please help me update my shipping address for order #4412?",
    "Where can I find the user manual for the wireless headset I purchased last week?",
    "Thank you so much! The replacement arrived today in perfect condition. Great support team!",
    "My order arrived on time and the shoes fit wonderfully. Very happy with the purchase.",
    "Order never arrived. Carrier claims it was delivered but my porch camera shows nothing. Please help!",
    "The item smells strongly of chemicals and caused skin irritation. Defective and dangerous product!",
    "How do I reset my password? I forgot which email was linked to this account.",
    "URGENT: Cancel order #5512 ASAP before it ships, I entered the wrong payment card!",
    "Tôi muốn hỏi về chính sách bảo hành sản phẩm máy xay sinh tố.", # Non-English ticket
    "Je voudrais savoir quand ma commande sera expédiée s'il vous plaît.", # Non-English ticket
]

def seed():
    print("Initializing SQLite database...")
    init_db(engine)

    aspects_yaml = backend_dir / "configs" / "aspects.yaml"
    taxonomy = Taxonomy.load_from_yaml(aspects_yaml)
    model = MockSentimentModel()

    print(f"Seeding {len(DEMO_TICKETS)} demo tickets into SQLite...")
    with SessionLocal() as db:
        for i, text in enumerate(DEMO_TICKETS, start=1):
            ticket = process_ticket_pipeline(
                raw_text=text,
                db=db,
                sentiment_model=model,
                priority_queue=None,
                taxonomy=taxonomy,
            )
            print(f"[{i:02d}] ID #{ticket.id} | Score: {ticket.priority_score:5.1f} | Level: {ticket.priority_level:8s} | Dominant: {ticket.dominant_aspect or 'none':16s} | Text: {text[:50]}...")

    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed()
