# """
# Free, local embeddings using sentence-transformers (no API key, no cost).
# Model is downloaded once and cached on disk.
# """
# from functools import lru_cache
# from sentence_transformers import SentenceTransformer
# from app.config import settings


# @lru_cache(maxsize=1)
# def get_embedder() -> SentenceTransformer:
#     return SentenceTransformer(settings.embedding_model)


# def embed_texts(texts: list[str]) -> list[list[float]]:
#     model = get_embedder()
#     vectors = model.encode(texts, normalize_embeddings=True)
#     return vectors.tolist()


# def embed_query(text: str) -> list[float]:
#     return embed_texts([text])[0]

from functools import lru_cache
from fastembed import TextEmbedding

DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"


@lru_cache(maxsize=1)
def get_embedder() -> TextEmbedding:
    return TextEmbedding(model_name=DEFAULT_MODEL)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedder()
    vectors = list(model.embed(texts))
    return [v.tolist() for v in vectors]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]