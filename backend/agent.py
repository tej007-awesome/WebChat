import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool

from backend.config import AGENT_MODEL, OPENROUTER_BASE_URL
from backend.retriever import retrieve_chunks

# Module-level state: set before each chat call
_current_url: str | None = None

SYSTEM_PROMPT = """\
You are a helpful assistant that answers questions about a specific website's content.

RULES:
1. ALWAYS use the search_website tool before answering. Never answer from your own knowledge.
2. Base answers ONLY on returned chunks. If chunks don't contain the answer, say so.
3. ALWAYS include inline citations using [Chunk N] format.
4. When using multiple chunks: "Founded in 2020 [Chunk 1] with 500 employees [Chunk 3]."
5. Never fabricate information not in the retrieved chunks.
"""


@tool
def search_website(query: str) -> str:
    """Search the ingested website content for information relevant to the query."""
    if _current_url is None:
        return "Error: No website has been ingested yet. Please ingest a URL first."

    chunks = retrieve_chunks(_current_url, query)

    if not chunks:
        return "No relevant content found for this query."

    parts = []
    for chunk in chunks:
        header = f"[Chunk {chunk['chunk_id']}] (score: {chunk['score']})"
        parts.append(f"{header}\n{chunk['text']}")

    return "\n---\n".join(parts)


def get_agent() -> Agent:
    """Create a new Agno agent instance."""
    return Agent(
        model=OpenAIChat(
            id=AGENT_MODEL,
            base_url=OPENROUTER_BASE_URL,
            api_key=os.environ["OPENROUTER_API_KEY"],
        ),
        tools=[search_website],
        instructions=SYSTEM_PROMPT,
        markdown=True,
    )
