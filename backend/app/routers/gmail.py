from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.core.security import get_current_user, require_admin
from app.services.gmail_service import build_oauth_flow
from app.config import settings

router = APIRouter(prefix="/api/gmail", tags=["gmail"])


@router.get("/oauth/start")
def oauth_start(_: models.User = Depends(require_admin)):
    flow = build_oauth_flow()
    auth_url, _state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )
    return {"auth_url": auth_url}


@router.get("/oauth/callback")
def oauth_callback(code: str, db: Session = Depends(get_db)):
    flow = build_oauth_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials

    import google.oauth2.id_token as id_token_lib
    import google.auth.transport.requests as g_requests
    # Lightweight: get email via Gmail profile endpoint instead of ID token
    from googleapiclient.discovery import build
    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId="me").execute()
    email_address = profile["emailAddress"]

    account = db.query(models.GmailAccount).filter(
        models.GmailAccount.email_address == email_address
    ).first()
    if not account:
        account = models.GmailAccount(email_address=email_address)
        db.add(account)

    account.access_token = creds.token
    account.refresh_token = creds.refresh_token or account.refresh_token
    account.is_active = True
    db.commit()

    return RedirectResponse(url=f"{settings.frontend_origin}/settings?gmail_connected=1")


@router.get("/accounts")
def list_accounts(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    accounts = db.query(models.GmailAccount).all()
    return [
        {"id": a.id, "email_address": a.email_address, "is_active": a.is_active}
        for a in accounts
    ]


@router.delete("/accounts/{account_id}")
def remove_account(account_id: str, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    account = db.query(models.GmailAccount).filter(models.GmailAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
    return {"ok": True}
