# analyzer/fetcher.py
# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 & 2 of the pipeline: Fetch → Clean
#
# Responsibilities:
#   - Send an HTTP GET request to a URL with browser-like headers
#   - Strip all HTML tags, scripts, navigation, and boilerplate
#   - Return clean plain text ready for NLP sentence splitting
# ─────────────────────────────────────────────────────────────────────────────

import re
import requests
from bs4 import BeautifulSoup

# Mimic a real Chrome browser so websites don't block the scraper with a 403
_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# HTML tags whose content is never part of the actual policy text
_NOISE_TAGS = ["script", "style", "nav", "footer", "header", "form", "button"]


def fetch_html(url: str, timeout: int = 15) -> str:
    """
    Sends an HTTP GET request and returns the raw HTML.

    Args:
        url     -- Full URL of the privacy policy page
        timeout -- Request timeout in seconds (default 15)

    Returns:
        Raw HTML string

    Raises:
        requests.HTTPError  -- If the server returns 4xx / 5xx
        requests.Timeout    -- If the request exceeds `timeout` seconds
    """
    print(f"[fetcher] Fetching: {url}")
    response = requests.get(url, headers=_BROWSER_HEADERS, timeout=timeout)
    response.raise_for_status()
    print(f"[fetcher] Received {len(response.text):,} characters of HTML")
    return response.text


def clean_html(html: str) -> str:
    """
    Strips HTML markup and returns clean, readable plain text.

    Steps:
      1. Parse HTML with the fast lxml parser
      2. Remove noise tags (scripts, nav, footer, etc.)
      3. Extract all remaining text with spaces between elements
      4. Collapse multiple whitespace characters into single spaces

    Args:
        html -- Raw HTML string from fetch_html()

    Returns:
        Normalized plain-text string
    """
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(_NOISE_TAGS):
        tag.decompose()

    raw_text = soup.get_text(separator=" ")
    cleaned  = re.sub(r'\s+', ' ', raw_text).strip()

    print(f"[fetcher] Cleaned to {len(cleaned):,} characters of plain text")
    return cleaned
