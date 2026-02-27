.PHONY: setup backend frontend

setup:
	uv sync

backend:
	uv run uvicorn backend.main:app --reload --port 8000

frontend:
	uv run streamlit run frontend/app.py --server.port 8501
