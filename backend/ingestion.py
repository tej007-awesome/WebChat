import os

from llama_index.core import Document, Settings, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from backend.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
    url_to_collection_name,
)


def ingest_text(url: str, text: str) -> dict:
    """Chunk, embed, and store text in Qdrant. Returns collection info."""
    collection_name = url_to_collection_name(url)

    # Configure embedding model (local HuggingFace model — no API key needed)
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)
    Settings.node_parser = SentenceSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    # Set up Qdrant vector store
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key = os.getenv("QDRANT_API_KEY") or None

    client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
    )
    vector_store = QdrantVectorStore(
        collection_name=collection_name,
        client=client,
    )

    # Create document with source metadata
    doc = Document(text=text, metadata={"source_url": url})

    # StorageContext required for Qdrant to actually persist vectors
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Index handles chunking → embedding → storage
    index = VectorStoreIndex.from_documents(
        [doc],
        storage_context=storage_context,
    )

    # Get chunk count from Qdrant (docstore is empty when using StorageContext)
    collection_info = client.get_collection(collection_name)
    num_chunks = collection_info.points_count

    return {"collection_name": collection_name, "num_chunks": num_chunks}
