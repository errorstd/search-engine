"""
tests/test_crawler.py

Unit tests for crawler.py.

These focus on the pure helper functions and avoid real HTTP requests.
"""

from __future__ import annotations

import os
import sys
from textwrap import dedent

# Ensure the project root (containing the 'src' package) is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.crawler import extract_text_from_page, find_next_page_url


def test_extract_text_from_page_includes_quotes_authors_and_tags():
    html = dedent(
        """
        <html>
          <body>
            <div class="quote">
              <span class="text">“Quote one.”</span>
              <span class="author">Author One</span>
              <div class="tags">
                <a class="tag">life</a>
                <a class="tag">inspirational</a>
              </div>
            </div>
            <div class="quote">
              <span class="text">“Quote two.”</span>
              <span class="author">Author Two</span>
              <div class="tags">
                <a class="tag">humor</a>
              </div>
            </div>
          </body>
        </html>
        """
    )

    text = extract_text_from_page(html)

    # The output is a single string; we just check that key parts are present.
    assert "Quote one." in text
    assert "Author One" in text
    assert "life" in text
    assert "inspirational" in text
    assert "Quote two." in text
    assert "Author Two" in text
    assert "humor" in text


def test_find_next_page_url_when_next_link_exists():
    html = dedent(
        """
        <html>
          <body>
            <ul class="pager">
              <li class="next">
                <a href="/page/2/">Next</a>
              </li>
            </ul>
          </body>
        </html>
        """
    )

    current_url = "https://quotes.toscrape.com/"
    next_url = find_next_page_url(html, current_url)

    assert next_url == "https://quotes.toscrape.com/page/2/"


def test_find_next_page_url_returns_none_when_no_next_link():
    html = dedent(
        """
        <html>
          <body>
            <ul class="pager">
              <li class="previous">
                <a href="/page/1/">Previous</a>
              </li>
            </ul>
          </body>
        </html>
        """
    )

    current_url = "https://quotes.toscrape.com/page/10/"
    next_url = find_next_page_url(html, current_url)

    assert next_url is None