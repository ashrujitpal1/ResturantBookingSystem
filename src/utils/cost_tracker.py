"""Cost tracking and observability utilities."""
import uuid
from datetime import datetime


def generate_correlation_id() -> str:
    """Generate unique correlation ID for request tracking."""
    return f"req_{uuid.uuid4()}"


def track_cost(correlation_id: str, user_id: str, tokens_used: int, model_name: str):
    """Track cost for observability (placeholder for actual implementation)."""
    # In production: send to CloudWatch/X-Ray
    print(f"💰 Cost tracking: {correlation_id} | User: {user_id} | Tokens: {tokens_used} | Model: {model_name}")


def scrub_pii(text: str) -> str:
    """Remove PII before storing in memory."""
    import re
    text = re.sub(r'\b\d{4}[\s\-]\d{4}[\s\-]\d{4}[\s\-]\d{4}\b', '<CARD>', text)
    text = re.sub(r'\+?\d[\d\s\-\(\)]{9,}', '<PHONE>', text)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '<EMAIL>', text)
    text = re.sub(r'booking_[a-f0-9]{8}', 'booking_<ID>', text)
    return text
