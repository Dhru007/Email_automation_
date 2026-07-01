from app.services.vector_store import query_similar
from app.services.groq_service import classify_and_score, generate_reply


def process_incoming_email(subject: str, body: str, category_hint: str | None = None) -> dict:
    """
    Full pipeline for one inbound email:
      1. Classify + sentiment + confidence (Groq)
      2. Retrieve top-k relevant KB chunks (Chroma, free local embeddings)
      3. Generate a grounded reply draft (Groq)
    Returns everything the API layer needs to persist + show in the dashboard.
    """
    classification = classify_and_score(body, subject)
    category = classification.get("category", "general_enquiry")

    kb_hits = query_similar(f"{subject}\n{body}", top_k=5)
    kb_texts = [h["text"] for h in kb_hits]

    draft = generate_reply(
        email_body=body,
        subject=subject,
        sentiment=classification.get("sentiment", "neutral"),
        category=category,
        kb_chunks=kb_texts,
    )

    return {
        "category": category,
        "sentiment": classification.get("sentiment", "neutral"),
        "intent": classification.get("intent", ""),
        "is_legal_risk": classification.get("is_legal_risk", False),
        "confidence": classification.get("confidence", 0.5),
        "draft": draft,
        "kb_chunks_used": kb_hits,
    }
