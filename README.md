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
                        (chunking +           Qdrant
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
| Embeddings | HuggingFace (`BAAI/bge-small-en-v1.5`) |
| Vector Store | Qdrant (Cloud or local) |
| Chunking | LlamaIndex SentenceSplitter |
| Scraping | Trafilatura |

## Setup

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenRouter API key (for the chat model)
- Qdrant URL (Cloud or local) and optional API key

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

## Logging

The app uses a shared logger configuration for backend and frontend.

Configure in `.env`:
```bash
LOG_DIR=logs
LOG_LEVEL=INFO
LOG_TO_CONSOLE=1
```

- `LOG_DIR`: directory for log files
- `LOG_LEVEL`: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- `LOG_TO_CONSOLE`: `1` to also print logs to terminal, `0` for file-only logs

Log files:
- `logs/webchat.log` (all logs)
- `logs/webchat.error.log` (errors only)

View logs:
```bash
tail -f logs/webchat.log
tail -f logs/webchat.error.log
```

## Docker

### Run (recommended)

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:8501
- Backend health: http://localhost:8000/health

Stop:
```bash
docker compose down
```

### Logs

- By default, Docker mounts `./logs` into containers so logs persist on your host.
- For Docker console logs, run:
  ```bash
  docker compose logs -f backend
  docker compose logs -f frontend
  ```

### Using local Qdrant (optional)

1. Uncomment the `qdrant` service in `docker-compose.yml`
2. Set these in `.env`:
   ```
   QDRANT_URL=http://qdrant:6333
   QDRANT_API_KEY=
   ```

### Run without Compose (advanced)

Build once:
```bash
docker build -t webchat .
```

Backend:
```bash
docker run --rm -p 8000:8000 --env-file .env webchat \
  uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Frontend (in another terminal):
```bash
docker run --rm -p 8501:8501 --env-file .env -e API_BASE=http://host.docker.internal:8000 webchat \
  streamlit run frontend/app.py --server.address=0.0.0.0 --server.port=8501
```

## Usage

1. Paste a public URL in the sidebar (e.g., a Wikipedia article)
2. Click **Ingest Website** — the app scrapes, chunks, and indexes the content
3. Ask questions in the chat — answers include `[Chunk N]` citations grounded in the page content
4. Ingest a new URL to switch contexts (chat history resets)
