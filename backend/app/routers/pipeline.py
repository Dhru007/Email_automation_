"""
Manual trigger + webhook endpoint that runs the full RAG pipeline on a single
inbound email. The APScheduler poller (scheduler.py) calls the same
processing function for emails pulled from Gmail.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.core.security import get_current_user
from app.services.rag_service import process_incoming_email
from app.services.escalation_service import should_escalate, ping_escalation

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


def run_pipeline_for_thread(db: Session, thread: models.EmailThread, subject: str, body: str):
    result = process_incoming_email(subject, body)

    thread.category = result["category"]
    thread.sentiment = result["sentiment"]
    thread.ai_confidence = result["confidence"]

    rules = db.query(models.EscalationRule).all()
    escalate = should_escalate(thread, result, rules)
    thread.status = models.EmailStatus.escalated if escalate else models.EmailStatus.auto_replied

    message = models.EmailMessage(
        thread_id=thread.id,
        direction="outbound",
        body="",
        ai_draft=result["draft"],
        kb_chunks_used=result["kb_chunks_used"],
        is_approved=False,
    )
    db.add(message)
    db.commit()

    if escalate:
        ping_escalation(thread, reason=result.get("intent", ""))

    return result


@router.post("/run/{thread_id}")
def run_manual(thread_id: str, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    thread = db.query(models.EmailThread).filter(models.EmailThread.id == thread_id).first()
    last_inbound = (
        db.query(models.EmailMessage)
        .filter(models.EmailMessage.thread_id == thread_id, models.EmailMessage.direction == "inbound")
        .order_by(models.EmailMessage.created_at.desc())
        .first()
    )
    body = last_inbound.body if last_inbound else ""
    return run_pipeline_for_thread(db, thread, thread.subject, body)
