"""
ChromaDB vector store wrapper.
Works in two modes:
  - persistent: local on-disk Chroma (good for Render's persistent disk)
  - http: connect to a remote/hosted Chroma server
We pass our own embeddings (from embedding_service) so Chroma does not need
its own embedding function / API key.
"""
import uuid
import chromadb
from app.config import settings
from app.services.embedding_service import embed_texts, embed_query

_client = None
_collection = None

COLLECTION_NAME = "knowledge_base"


def get_client():
    global _client
    if _client is None:
        import chromadb   # moved inside — lazy load
        if settings.chroma_mode == "http":
            _client = chromadb.HttpClient(...)
        else:
            _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return _client

def get_collection():
    global _collection
    if _collection is None:
        _collection = get_client().get_or_create_collection(name=COLLECTION_NAME)
    return _collection


def add_chunks(article_id: str, title: str, category_tags: list[str], chunks: list[str]):
    collection = get_collection()
    ids = [f"{article_id}-{i}-{uuid.uuid4().hex[:6]}" for i in range(len(chunks))]
    embeddings = embed_texts(chunks)
    metadatas = [
        {"article_id": article_id, "title": title, "tags": ",".join(category_tags)}
        for _ in chunks
    ]
    collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
    return ids


def query_similar(query: str, top_k: int = 5, category_filter: str | None = None):
    collection = get_collection()
    query_embedding = embed_query(query)
    where = {"tags": {"$contains": category_filter}} if category_filter else None
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where,
    )
    hits = []
    for doc, meta, dist in zip(
        results.get("documents", [[]])[0],
        results.get("metadatas", [[]])[0],
        results.get("distances", [[]])[0],
    ):
        hits.append({"text": doc, "metadata": meta, "score": 1 - dist})
    return hits


def delete_article_chunks(article_id: str):
    collection = get_collection()
    collection.delete(where={"article_id": article_id})
