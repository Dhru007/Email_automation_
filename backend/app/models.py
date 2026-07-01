import uuid
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, Float, DateTime, ForeignKey, Enum, Integer, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    admin = "admin"
    agent = "agent"


class EmailCategory(str, enum.Enum):
    legal = "legal"
    product_issue = "product_issue"
    delivery_issue = "delivery_issue"
    return_refund = "return_refund"
    billing = "billing"
    general_enquiry = "general_enquiry"
    feedback_praise = "feedback_praise"
    spam = "spam"


class EmailSentiment(str, enum.Enum):
    angry = "angry"
    frustrated = "frustrated"
    sad = "sad"
    neutral = "neutral"
    happy = "happy"


class EmailStatus(str, enum.Enum):
    open = "open"
    replied = "replied"
    escalated = "escalated"
    auto_replied = "auto_replied"


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    name = Column(String, default="")
    role = Column(Enum(UserRole), default=UserRole.agent)
    is_vip_watcher = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class GmailAccount(Base):
    __tablename__ = "gmail_accounts"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email_address = Column(String, unique=True, nullable=False)
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expiry = Column(DateTime, nullable=True)
    history_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    connected_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class EmailThread(Base):
    __tablename__ = "email_threads"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    gmail_thread_id = Column(String, index=True)
    gmail_account_id = Column(UUID(as_uuid=False), ForeignKey("gmail_accounts.id"))
    sender_email = Column(String, index=True)
    sender_name = Column(String, default="")
    subject = Column(String, default="")
    is_vip = Column(Boolean, default=False)
    contact_count = Column(Integer, default=1)
    category = Column(Enum(EmailCategory), nullable=True)
    sentiment = Column(Enum(EmailSentiment), nullable=True)
    status = Column(Enum(EmailStatus), default=EmailStatus.open)
    ai_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("EmailMessage", back_populates="thread", cascade="all, delete-orphan")


class EmailMessage(Base):
    __tablename__ = "email_messages"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    thread_id = Column(UUID(as_uuid=False), ForeignKey("email_threads.id"))
    gmail_message_id = Column(String, index=True)
    direction = Column(String, default="inbound")  # inbound | outbound
    body = Column(Text)
    attachments = Column(JSON, default=list)
    ai_draft = Column(Text, nullable=True)
    kb_chunks_used = Column(JSON, default=list)  # list of chunk ids/snippets
    is_approved = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    thread = relationship("EmailThread", back_populates="messages")


class KnowledgeBaseArticle(Base):
    __tablename__ = "kb_articles"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    title = Column(String, nullable=False)
    source_type = Column(String, default="manual")  # manual | pdf | docx | notion | zendesk
    category_tags = Column(JSON, default=list)
    raw_text = Column(Text)
    chunk_count = Column(Integer, default=0)
    uploaded_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class EscalationRule(Base):
    __tablename__ = "escalation_rules"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String)
    category = Column(Enum(EmailCategory), nullable=True)
    min_sentiment_severity = Column(String, nullable=True)  # angry, frustrated...
    min_contact_count = Column(Integer, nullable=True)
    confidence_threshold = Column(Float, default=0.70)
    is_active = Column(Boolean, default=True)


class AppSettings(Base):
    __tablename__ = "app_settings"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    key = Column(String, unique=True, nullable=False)
    value = Column(JSON)
