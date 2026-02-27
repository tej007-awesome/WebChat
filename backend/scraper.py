import trafilatura


def scrape_url(url: str) -> str:
    """Scrape a URL and return clean text content."""
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        raise ValueError(f"Failed to fetch URL: {url}")

    text = trafilatura.extract(
        downloaded,
        favor_recall=True,
        include_tables=True,
    )

    if not text or len(text) < 50:
        raise ValueError(
            f"Could not extract meaningful content from {url}. "
            "The page may be JavaScript-rendered or require authentication."
        )

    return text
