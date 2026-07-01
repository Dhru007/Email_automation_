from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app import models, schemas
from app.core.security import get_current_user
from app.services.gmail_service import get_gmail_service, send_reply

router = APIRouter(prefix="/api/emails", tags=["emails"])


@router.get("/threads", response_model=list[schemas.EmailThreadOut])
def list_threads(
    category: str | None = None,
    sentiment: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    q = db.query(models.EmailThread).options(joinedload(models.EmailThread.messages))
    if category:
        q = q.filter(models.EmailThread.category == category)
    if sentiment:
        q = q.filter(models.EmailThread.sentiment == sentiment)
    if status:
        q = q.filter(models.EmailThread.status == status)
    return q.order_by(models.EmailThread.updated_at.desc()).all()


@router.get("/threads/{thread_id}", response_model=schemas.EmailThreadOut)
def get_thread(thread_id: str, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    thread = db.query(models.EmailThread).options(
        joinedload(models.EmailThread.messages)
    ).filter(models.EmailThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread


@router.post("/approve-send")
def approve_and_send(payload: schemas.ApproveDraftRequest, db: Session = Depends(get_db),
                      _: models.User = Depends(get_current_user)):
    message = db.query(models.EmailMessage).filter(models.EmailMessage.id == payload.message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    thread = db.query(models.EmailThread).filter(models.EmailThread.id == message.thread_id).first()
    account = db.query(models.GmailAccount).filter(
        models.GmailAccount.id == thread.gmail_account_id
    ).first()

    final_body = payload.edited_body or message.ai_draft
    if account:
        service = get_gmail_service(account)
        send_reply(service, to=thread.sender_email, subject=thread.subject,
                   body=final_body, thread_id=thread.gmail_thread_id)

    message.body = final_body
    message.is_approved = True
    thread.status = models.EmailStatus.replied
    db.commit()
    return {"ok": True}
