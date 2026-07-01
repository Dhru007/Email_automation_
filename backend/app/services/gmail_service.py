"""
Gmail API integration.
- OAuth 2.0 flow to connect an inbox
- Polling for new messages (called by APScheduler every N seconds, see scheduler.py)
- Auto-labels processed emails so they are not re-processed
"""
import base64
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app.config import settings

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/userinfo.email",
]
PROCESSED_LABEL = "AI-Processed"


def build_oauth_flow() -> Flow:
    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.google_redirect_uri],
        }
    }
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = settings.google_redirect_uri
    return flow


def credentials_from_account(account) -> Credentials:
    creds = Credentials(
        token=account.access_token,
        refresh_token=account.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=SCOPES,
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        account.access_token = creds.token
    return creds


def get_gmail_service(account):
    creds = credentials_from_account(account)
    return build("gmail", "v1", credentials=creds)


def ensure_processed_label(service) -> str:
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    for label in labels:
        if label["name"] == PROCESSED_LABEL:
            return label["id"]
    created = service.users().labels().create(
        userId="me", body={"name": PROCESSED_LABEL}
    ).execute()
    return created["id"]


def list_new_messages(service, max_results: int = 20):
    """Fetch unread/unprocessed messages from inbox."""
    query = f"-label:{PROCESSED_LABEL.lower().replace(' ', '-')} in:inbox"
    resp = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    return resp.get("messages", [])


def get_message_detail(service, message_id: str) -> dict:
    msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
    body = _extract_body(msg["payload"])
    return {
        "id": msg["id"],
        "thread_id": msg["threadId"],
        "from": headers.get("From", ""),
        "subject": headers.get("Subject", ""),
        "body": body,
    }


def _extract_body(payload: dict) -> str:
    if payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
    for part in payload.get("parts", []):
        text = _extract_body(part)
        if text:
            return text
    return ""


def mark_processed(service, message_id: str, label_id: str):
    service.users().messages().modify(
        userId="me", id=message_id, body={"addLabelIds": [label_id]}
    ).execute()


def send_reply(service, to: str, subject: str, body: str, thread_id: str | None = None):
    import email.mime.text as mime_text
    message = mime_text.MIMEText(body)
    message["to"] = to
    message["subject"] = f"Re: {subject}" if not subject.lower().startswith("re:") else subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    payload = {"raw": raw}
    if thread_id:
        payload["threadId"] = thread_id
    return service.users().messages().send(userId="me", body=payload).execute()
