from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str = ""
    role: str = "agent"


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    role: str
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class EmailMessageOut(BaseModel):
    id: str
    direction: str
    body: str
    ai_draft: Optional[str] = None
    kb_chunks_used: Optional[List[Any]] = None
    is_approved: bool
    created_at: datetime
    class Config:
        from_attributes = True


class EmailThreadOut(BaseModel):
    id: str
    sender_email: str
    sender_name: str
    subject: str
    is_vip: bool
    contact_count: int
    category: Optional[str] = None
    sentiment: Optional[str] = None
    status: str
    ai_confidence: Optional[float] = None
    created_at: datetime
    messages: List[EmailMessageOut] = []
    class Config:
        from_attributes = True


class ApproveDraftRequest(BaseModel):
    message_id: str
    edited_body: Optional[str] = None


class KBArticleCreate(BaseModel):
    title: str
    raw_text: str
    category_tags: List[str] = []


class KBArticleOut(BaseModel):
    id: str
    title: str
    source_type: str
    category_tags: List[str]
    chunk_count: int
    created_at: datetime
    class Config:
        from_attributes = True


class KBPreviewRequest(BaseModel):
    query: str
    top_k: int = 5


class EscalationRuleCreate(BaseModel):
    name: str
    category: Optional[str] = None
    min_sentiment_severity: Optional[str] = None
    min_contact_count: Optional[int] = None
    confidence_threshold: float = 0.70


class AnalyticsSummary(BaseModel):
    total_emails: int
    auto_replied: int
    escalated: int
    avg_response_time_seconds: Optional[float] = None
    category_breakdown: dict
    sentiment_trend: list
