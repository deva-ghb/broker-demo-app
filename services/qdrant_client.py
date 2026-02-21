"""
Qdrant vector database client.
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from settings import settings

_qdrant_client: QdrantClient = None

PROPERTY_COLLECTION = "properties"
EMBEDDING_DIM = 3072  # text-embedding-3-large dimension


def get_qdrant() -> QdrantClient:
    """Get the Qdrant client singleton."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
        )
    return _qdrant_client


async def init_qdrant_collections():
    """Create Qdrant collections if they don't exist."""
    client = get_qdrant()
    collections = [c.name for c in client.get_collections().collections]

    if PROPERTY_COLLECTION not in collections:
        client.create_collection(
            collection_name=PROPERTY_COLLECTION,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE,
            ),
        )
        print(f"✅ Created Qdrant collection: {PROPERTY_COLLECTION}")
    else:
        print(f"ℹ️  Qdrant collection '{PROPERTY_COLLECTION}' already exists")


def close_qdrant():
    """Close the Qdrant client."""
    global _qdrant_client
    if _qdrant_client:
        _qdrant_client.close()
        _qdrant_client = None
        print("🔌 Qdrant connection closed")
