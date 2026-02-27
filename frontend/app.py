import httpx
import streamlit as st

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="WebChat", page_icon="🌐", layout="wide")
st.title("WebChat — Chat with Any Website")

# ── Sidebar: URL ingestion ──────────────────────────────────────────
with st.sidebar:
    st.header("Website Setup")
    url = st.text_input("Paste a public URL:", placeholder="https://en.wikipedia.org/wiki/...")

    if st.button("Ingest Website", type="primary", disabled=not url):
        with st.spinner("Scraping and indexing... this may take a minute."):
            try:
                resp = httpx.post(
                    f"{API_BASE}/ingest",
                    json={"url": url},
                    timeout=120.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"Ingested **{data['num_chunks']}** chunks!")
                    st.session_state["active_url"] = url
                    st.session_state["messages"] = []
                else:
                    detail = resp.json().get("detail", resp.text)
                    st.error(f"Ingestion failed: {detail}")
            except httpx.TimeoutException:
                st.error("Request timed out. The page may be too large.")
            except httpx.ConnectError:
                st.error("Cannot connect to backend. Is it running on port 8000?")

    if active := st.session_state.get("active_url"):
        st.divider()
        st.caption(f"Active URL: {active}")

# ── Main chat area ──────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if not st.session_state.get("active_url"):
    st.info("Paste a URL in the sidebar and click **Ingest Website** to get started.")
else:
    # Render chat history
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about the website..."):
        # Show user message
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    resp = httpx.post(
                        f"{API_BASE}/chat",
                        json={
                            "url": st.session_state["active_url"],
                            "message": prompt,
                        },
                        timeout=60.0,
                    )
                    if resp.status_code == 200:
                        answer = resp.json()["response"]
                    else:
                        answer = f"Error: {resp.json().get('detail', resp.text)}"
                except httpx.TimeoutException:
                    answer = "Request timed out. Please try again."
                except httpx.ConnectError:
                    answer = "Cannot connect to backend. Is it running on port 8000?"

            st.markdown(answer)
            st.session_state["messages"].append({"role": "assistant", "content": answer})
