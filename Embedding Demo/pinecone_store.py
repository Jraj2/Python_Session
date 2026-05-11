from pinecone import Pinecone, ServerlessSpec
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME, EMBEDDING_DIMENSIONS

_pc = Pinecone(api_key=PINECONE_API_KEY)


def init_index():
    existing = [idx.name for idx in _pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing:
        print(f"Creating Pinecone index '{PINECONE_INDEX_NAME}' (dim={EMBEDDING_DIMENSIONS})...")
        _pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=EMBEDDING_DIMENSIONS,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        print("  Index created.")
    return _pc.Index(PINECONE_INDEX_NAME)


def upsert_item(index, id: str, vector: list[float], metadata: dict):
    index.upsert(vectors=[{"id": id, "values": vector, "metadata": metadata}])


def query(index, vector: list[float], top_k: int = 5) -> list[dict]:
    result = index.query(vector=vector, top_k=top_k, include_metadata=True)
    return [{"id": m.id, "score": m.score, "metadata": m.metadata} for m in result.matches]
