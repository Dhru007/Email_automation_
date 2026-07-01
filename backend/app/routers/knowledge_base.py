from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.core.security import get_current_user
from app.services.chunking_service import chunk_text
from app.services.vector_store import add_chunks, delete_article_chunks, query_similar
from pypdf import PdfReader
import docx as docx_lib
import io

router = APIRouter(prefix="/api/kb", tags=["knowledge-base"])


def _extract_text(filename: str, raw: bytes) -> str:
    if filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(raw))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if filename.endswith(".docx"):
        d = docx_lib.Document(io.BytesIO(raw))
        return "\n".join(p.text for p in d.paragraphs)
    return raw.decode("utf-8", errors="ignore")


@router.get("/articles", response_model=list[schemas.KBArticleOut])
def list_articles(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.KnowledgeBaseArticle).order_by(
        models.KnowledgeBaseArticle.created_at.desc()
    ).all()


@router.post("/articles/manual", response_model=schemas.KBArticleOut)
def add_manual_article(payload: schemas.KBArticleCreate, db: Session = Depends(get_db),
                        user: models.User = Depends(get_current_user)):
    article = models.KnowledgeBaseArticle(
        title=payload.title, source_type="manual",
        category_tags=payload.category_tags, raw_text=payload.raw_text,
        uploaded_by=user.id,
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    chunks = chunk_text(payload.raw_text)
    add_chunks(article.id, article.title, payload.category_tags, chunks)
    article.chunk_count = len(chunks)
    db.commit()
    db.refresh(article)
    return article


@router.post("/articles/upload", response_model=schemas.KBArticleOut)
async def upload_article(
    file: UploadFile = File(...),
    category_tags: str = Form(""),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    raw = await file.read()
    text = _extract_text(file.filename, raw)
    tags = [t.strip() for t in category_tags.split(",") if t.strip()]
    source_type = "pdf" if file.filename.endswith(".pdf") else (
        "docx" if file.filename.endswith(".docx") else "manual"
    )

    article = models.KnowledgeBaseArticle(
        title=file.filename, source_type=source_type,
        category_tags=tags, raw_text=text, uploaded_by=user.id,
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    chunks = chunk_text(text)
    add_chunks(article.id, article.title, tags, chunks)
    article.chunk_count = len(chunks)
    db.commit()
    db.refresh(article)
    return article


@router.delete("/articles/{article_id}")
def delete_article(article_id: str, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    article = db.query(models.KnowledgeBaseArticle).filter(
        models.KnowledgeBaseArticle.id == article_id
    ).first()
    if article:
        delete_article_chunks(article_id)
        db.delete(article)
        db.commit()
    return {"ok": True}


@router.post("/preview")
def preview_chunks(payload: schemas.KBPreviewRequest, _: models.User = Depends(get_current_user)):
    """Lets an admin see which KB chunks would be retrieved for a sample email."""
    return query_similar(payload.query, top_k=payload.top_k)
