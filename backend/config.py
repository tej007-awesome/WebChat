import hashlib
import re
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

# Chunking
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64

# Models
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
AGENT_MODEL = "google/gemini-2.0-flash-001"

# OpenRouter
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Retrieval
TOP_K = 5


def normalize_url(url: str) -> str:
    """Normalize a URL to prevent mismatches from trailing slashes, missing scheme, etc."""
    url = url.strip().rstrip("/")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def url_to_collection_name(url: str) -> str:
    """Convert a URL to a deterministic Qdrant collection name."""
    url = normalize_url(url)
    parsed = urlparse(url)
    domain = re.sub(r"[^a-zA-Z0-9]", "_", parsed.netloc)
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:12]
    return f"webchat_{domain}_{url_hash}"
