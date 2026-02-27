import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend import agent as agent_module
from backend.config import normalize_url
from backend.ingestion import ingest_text
from backend.scraper import scrape_url
from logger import setup_logging

setup_logging("webchat")
logger = logging.getLogger("webchat.api")

app = FastAPI(title="WebChat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory agent store: url -> Agent
_agents: dict[str, object] = {}


class IngestRequest(BaseModel):
    url: str


class ChatRequest(BaseModel):
    url: str
    message: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.middleware("http")
async def request_logging(request: Request, call_next):
    import time

    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("[REQUEST] %s %s -> exception", request.method, request.url.path)
        raise

    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "[REQUEST] %s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        getattr(response, "status_code", "?"),
        duration_ms,
    )
    return response


@app.post("/ingest")
def ingest(req: IngestRequest):
    url = normalize_url(req.url)
    logger.info(f"[INGEST] normalized url: {url!r}")

    try:
        text = scrape_url(url)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        result = ingest_text(url, text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

    logger.info(f"[INGEST] collection: {result['collection_name']}, chunks: {result['num_chunks']}")

    # Clear cached agent for this URL so it picks up fresh data
    _agents.pop(url, None)

    return {
        "status": "ok",
        "url": url,
        "collection_name": result["collection_name"],
        "num_chunks": result["num_chunks"],
    }


@app.post("/chat")
def chat(req: ChatRequest):
    url = normalize_url(req.url)
    logger.info(f"[CHAT] normalized url: {url!r}")

    # Set the current URL for the retrieval tool
    agent_module._current_url = url

    # Get or create agent for this URL
    if url not in _agents:
        _agents[url] = agent_module.get_agent()

    ag = _agents[url]
    response = ag.run(req.message)

    return {
        "response": response.content,
        "url": url,
    }
