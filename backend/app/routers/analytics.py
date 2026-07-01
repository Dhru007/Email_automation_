from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models
from app.core.security import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
def summary(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    threads = db.query(models.EmailThread).all()
    total = len(threads)
    auto_replied = sum(1 for t in threads if t.status == models.EmailStatus.auto_replied)
    escalated = sum(1 for t in threads if t.status == models.EmailStatus.escalated)

    category_breakdown = dict(Counter(t.category.value for t in threads if t.category))
    sentiment_counter = Counter(t.sentiment.value for t in threads if t.sentiment)

    return {
        "total_emails": total,
        "auto_replied": auto_replied,
        "escalated": escalated,
        "category_breakdown": category_breakdown,
        "sentiment_trend": [{"sentiment": k, "count": v} for k, v in sentiment_counter.items()],
    }


@router.get("/top-escalation-reasons")
def top_escalation_reasons(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    threads = db.query(models.EmailThread).filter(
        models.EmailThread.status == models.EmailStatus.escalated
    ).all()
    reasons = Counter()
    for t in threads:
        if t.category and t.category.value == "legal":
            reasons["legal_risk"] += 1
        elif t.is_vip:
            reasons["vip_customer"] += 1
        elif t.ai_confidence is not None and t.ai_confidence < 0.70:
            reasons["low_ai_confidence"] += 1
        elif t.sentiment and t.sentiment.value == "angry":
            reasons["angry_repeat_contact"] += 1
        else:
            reasons["other"] += 1
    return [{"reason": k, "count": v} for k, v in reasons.items()]
