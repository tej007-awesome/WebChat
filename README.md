# WebChat — Chat with Any Website

A full-stack RAG application that lets you paste any public URL, scrapes and indexes its content, then provides a chat interface where an AI answers questions with inline citations grounded only in the scraped content.

## Architecture

```
User → Streamlit UI → FastAPI Backend → Agno Agent ( OpenRouter model)
                                ↓               ↓
                         Trafilatura      search_website tool
                        (scraping)              ↓
                                ↓         LlamaIndex Retriever
                         LlamaIndex             ↓
                        (chunking +       Qdrant Cloud
                         embedding)      (vector search)
```

**Citation Flow:**
1. Ingestion: Document → SentenceSplitter → Chunks with metadata → Qdrant
2. Retrieval: Query → Qdrant similarity search → Top-K chunks labeled [Chunk 1..N]
3. Synthesis: Agent receives labeled chunks → System prompt enforces [Chunk N] citations
4. Display: Streamlit renders markdown with inline citations

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI + Uvicorn |
| Agent | Agno + Gemini |
| Model Provider | OpenRouter |
| Embeddings | OpenAI text-embedding-3-small |
| Vector Store | Qdrant Cloud |
| Chunking | LlamaIndex SentenceSplitter |
| Scraping | Trafilatura |

## Setup

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenRouter API key (for GPT-4o)
- OpenAI API key (for embeddings)
- Qdrant Cloud cluster URL and API key

### Install

```bash
# Clone the repo
git clone <repo-url> && cd webchat

# Install dependencies
make setup

# Configure environment variables
cp .env.example .env  # Edit with your actual keys
```

Edit `.env` with your credentials:
```
OPENROUTER_API_KEY=your-openrouter-key
QDRANT_URL=https://your-cluster.cloud.qdrant.io:6333
QDRANT_API_KEY=your-api-key
API_BASE=http://localhost:8000
```

### Run

Terminal 1 — Backend:
```bash
make backend
```

Terminal 2 — Frontend:
```bash
make frontend
```

Open http://localhost:8501 in your browser.

## Docker

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:8501
- Backend health: http://localhost:8000/health

## Usage

1. Paste a public URL in the sidebar (e.g., a Wikipedia article)
2. Click **Ingest Website** — the app scrapes, chunks, and indexes the content
3. Ask questions in the chat — answers include `[Chunk N]` citations grounded in the page content
4. Ingest a new URL to switch contexts (chat history resets)
