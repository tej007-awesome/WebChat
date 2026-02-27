FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# uv is used to install from uv.lock deterministically.
RUN python -m pip install --no-cache-dir uv

# Install deps first (better Docker layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONPATH="/app"

COPY backend ./backend
COPY frontend ./frontend
COPY README.md LICENSE ./

EXPOSE 8000 8501
