"""
Thin wrapper around the Groq Chat Completions API.
Model: llama-3.3-70b-versatile, temperature 0.5 (set in .env, overridable).
"""
import json
from groq import Groq
from app.config import settings

_client = None


def get_groq_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=settings.groq_api_key)
    return _client


def chat_completion(messages: list[dict], temperature: float | None = None,
                     response_format_json: bool = False) -> str:
    client = get_groq_client()
    kwargs = {
        "model": settings.groq_model,
        "messages": messages,
        "temperature": temperature if temperature is not None else settings.groq_temperature,
        "max_tokens": 1024,
    }
    if response_format_json:
        kwargs["response_format"] = {"type": "json_object"}

    completion = client.chat.completions.create(**kwargs)
    return completion.choices[0].message.content


def classify_and_score(email_body: str, subject: str) -> dict:
    """
    Single Groq call that returns category, sentiment, intent flags and
    a confidence score, as strict JSON.
    """
    system_prompt = (
        "You are an email triage engine for a customer support inbox. "
        "Classify the email and respond ONLY with a JSON object with keys: "
        "category (one of: legal, product_issue, delivery_issue, return_refund, "
        "billing, general_enquiry, feedback_praise, spam), "
        "sentiment (one of: angry, frustrated, sad, neutral, happy), "
        "intent (short string describing what the customer wants), "
        "is_legal_risk (boolean), "
        "confidence (float 0-1, how confident you are in this classification)."
    )
    user_prompt = f"Subject: {subject}\n\nBody:\n{email_body}"
    raw = chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format_json=True,
    )
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "category": "general_enquiry",
            "sentiment": "neutral",
            "intent": "unknown",
            "is_legal_risk": False,
            "confidence": 0.4,
        }


def generate_reply(email_body: str, subject: str, sentiment: str, category: str,
                    kb_chunks: list[str]) -> str:
    """
    RAG-grounded reply generation. Tone adapts based on sentiment/category.
    """
    tone_map = {
        "angry": "firm, empathetic, and solution-first",
        "frustrated": "acknowledging the delay, offering a clear resolution",
        "sad": "warm, human, and reassuring",
        "neutral": "professional and concise",
        "happy": "friendly and brand-forward",
    }
    if category == "legal":
        tone = "formal, careful, and non-committal on liability"
    else:
        tone = tone_map.get(sentiment, "professional and concise")

    context_block = "\n\n---\n\n".join(kb_chunks) if kb_chunks else "No KB articles matched."

    system_prompt = (
        "You are a customer support assistant drafting an email reply. "
        f"Tone must be: {tone}. "
        "Only use facts from the knowledge base context provided below — do not invent policies, "
        "prices, or timelines. If the KB does not cover the question, say a human will follow up. "
        "Keep the reply concise and ready to send.\n\n"
        f"KNOWLEDGE BASE CONTEXT:\n{context_block}"
    )
    user_prompt = f"Customer email — Subject: {subject}\n\n{email_body}\n\nDraft the reply."

    return chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
