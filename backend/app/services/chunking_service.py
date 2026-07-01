"""
Free text chunking using langchain-text-splitters (no API key needed).
Recursive splitter respects paragraph / sentence boundaries where possible.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=120,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def chunk_text(text: str) -> list[str]:
    chunks = splitter.split_text(text)
    return [c.strip() for c in chunks if c.strip()]
