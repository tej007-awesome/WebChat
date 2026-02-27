import logging
import os

from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from backend.config import EMBEDDING_MODEL, TOP_K, url_to_collection_name

logger = logging.getLogger("webchat")


def retrieve_chunks(url: str, query: str) -> list[dict]:
    """Retrieve relevant chunks from Qdrant for a given query."""
    collection_name = url_to_collection_name(url)
    logger.info(f"[RETRIEVER] url={url!r} -> collection={collection_name!r}")

    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)

    client = QdrantClient(
        url=os.environ["QDRANT_URL"],
        api_key=os.environ["QDRANT_API_KEY"],
    )
    vector_store = QdrantVectorStore(
        collection_name=collection_name,
        client=client,
    )

    # Reconstruct index from existing collection
    index = VectorStoreIndex.from_vector_store(vector_store)
    retriever = index.as_retriever(similarity_top_k=TOP_K)

    nodes = retriever.retrieve(query)

    return [
        {
            "chunk_id": i + 1,
            "text": node.get_text(),
            "source_url": node.metadata.get("source_url", url),
            "score": round(node.score, 4) if node.score else None,
        }
        for i, node in enumerate(nodes)
    ]
