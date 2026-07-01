from sqlalchemy.orm import Session
from app import models
import httpx
from app.config import settings


def should_escalate(thread: models.EmailThread, ai_result: dict, rules: list[models.EscalationRule]) -> bool:
    if ai_result.get("is_legal_risk") or ai_result.get("category") == "legal":
        return True
    if ai_result.get("confidence", 1.0) < 0.70:
        return True
    if thread.is_vip:
        return True
    if ai_result.get("sentiment") == "angry" and thread.contact_count >= 3:
        return True
    for rule in rules:
        if not rule.is_active:
            continue
        if rule.category and rule.category.value != ai_result.get("category"):
            continue
        if rule.min_contact_count and thread.contact_count < rule.min_contact_count:
            continue
        if ai_result.get("confidence", 1.0) < rule.confidence_threshold:
            return True
    return False


def ping_escalation(thread: models.EmailThread, reason: str):
    """In-app notification is just a DB status flip (read by dashboard via polling).
    Optionally also pings a Slack/Teams webhook if configured."""
    if settings.slack_webhook_url:
        try:
            httpx.post(
                settings.slack_webhook_url,
                json={"text": f"🚨 Escalation: {thread.subject} from {thread.sender_email} — {reason}"},
                timeout=5,
            )
        except Exception:
            pass
