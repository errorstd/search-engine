"""
crawler.py

Crawls https://quotes.toscrape.com/ and returns a list of pages
with their IDs, URLs, and extracted text content.

Respects a politeness window between successive HTTP requests.
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://quotes.toscrape.com/"
DEFAULT_DELAY_SECONDS = 6


def fetch_page(url: str, timeout: int = 10) -> str:
    """
    Fetch a single page and return its HTML as text.

    Raises requests.HTTPError on non-200 responses.
    """
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text


def extract_text_from_page(html: str) -> str:
    """
    Extract the main textual content from a quotes.toscrape.com page.

    For simplicity, we include:
    - quote texts
    - author names
    - tags

    Returns a single string with newline separators.
    """
    soup = BeautifulSoup(html, "html.parser")

    quotes = [q.get_text(separator=" ", strip=True) for q in soup.select(".quote .text")]
    authors = [a.get_text(strip=True) for a in soup.select(".quote .author")]
    tags = [t.get_text(strip=True) for t in soup.select(".quote .tags .tag")]

    parts: List[str] = []
    parts.extend(quotes)
    parts.extend(authors)
    parts.extend(tags)

    return "\n".join(parts)


def find_next_page_url(html: str, current_url: str) -> Optional[str]:
    """
    Find the absolute URL of the 'next' page, if it exists.

    Returns None if there is no next page.
    """
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("li.next a")
    if not next_link:
        return None

    href = next_link.get("href")
    if not href:
        return None

    return urljoin(current_url, href)


def crawl_website(
    base_url: str = BASE_URL,
    delay_seconds: int = DEFAULT_DELAY_SECONDS,
) -> List[Dict[str, str]]:
    """
    Crawl all pages starting from base_url, following 'Next' links.

    Returns a list of dicts:
        [
            {"page_id": 0, "url": "...", "text": "..."},
            {"page_id": 1, "url": "...", "text": "..."},
            ...
        ]

    Respects the given delay_seconds between successive HTTP requests.
    """
    pages: List[Dict[str, str]] = []
    current_url = base_url
    page_id = 0

    while current_url:
        try:
            html = fetch_page(current_url)
        except requests.RequestException as exc:
            print(f"[crawler] Error fetching {current_url}: {exc}")
            break

        text = extract_text_from_page(html)
        pages.append({"page_id": page_id, "url": current_url, "text": text})

        next_url = find_next_page_url(html, current_url)
        if not next_url:
            break

        page_id += 1

        # Respect politeness window between successive requests
        time.sleep(delay_seconds)
        current_url = next_url

    return pages