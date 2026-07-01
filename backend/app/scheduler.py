"""
Background polling job: every GMAIL_POLL_INTERVAL_SECONDS (default 60s),
pull new messages from every connected Gmail account, run the AI pipeline,
and label them as processed so they aren't picked up twice.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app import models
from app.config import settings
from app.services.gmail_service import (
    get_gmail_service, ensure_processed_label, list_new_messages,
    get_message_detail, mark_processed,
)
from app.routers.pipeline import run_pipeline_for_thread

scheduler = BackgroundScheduler()


def poll_all_accounts():
    db = SessionLocal()
    try:
        accounts = db.query(models.GmailAccount).filter(models.GmailAccount.is_active.is_(True)).all()
        for account in accounts:
            try:
                service = get_gmail_service(account)
                label_id = ensure_processed_label(service)
                for msg_ref in list_new_messages(service):
                    detail = get_message_detail(service, msg_ref["id"])
                    sender_email = detail["from"]

                    thread = db.query(models.EmailThread).filter(
                        models.EmailThread.gmail_thread_id == detail["thread_id"]
                    ).first()
                    if not thread:
                        thread = models.EmailThread(
                            gmail_thread_id=detail["thread_id"],
                            gmail_account_id=account.id,
                            sender_email=sender_email,
                            subject=detail["subject"],
                            contact_count=1,
                        )
                        db.add(thread)
                    else:
                        thread.contact_count += 1
                    db.commit()
                    db.refresh(thread)

                    inbound = models.EmailMessage(
                        thread_id=thread.id,
                        gmail_message_id=detail["id"],
                        direction="inbound",
                        body=detail["body"],
                    )
                    db.add(inbound)
                    db.commit()

                    run_pipeline_for_thread(db, thread, detail["subject"], detail["body"])
                    mark_processed(service, detail["id"], label_id)
            except Exception as e:
                print(f"[poller] error for account {account.email_address}: {e}")
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        poll_all_accounts, "interval",
        seconds=settings.gmail_poll_interval_seconds,
        id="gmail_poller", replace_existing=True,
    )
    scheduler.start()
