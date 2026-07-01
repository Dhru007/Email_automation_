from functools import lru_cache

DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"


@lru_cache(maxsize=1)
def get_embedder():
    from fastembed import TextEmbedding   # moved inside — lazy load
    return TextEmbedding(model_name=DEFAULT_MODEL)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedder()
    vectors = list(model.embed(texts))
    return [v.tolist() for v in vectors]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]