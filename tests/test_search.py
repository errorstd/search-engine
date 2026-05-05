"""
tests/test_search.py

Unit tests for search.py, using a small in-memory index built
via indexer.build_index().
"""

from __future__ import annotations

import os
import sys

# Ensure the project root (containing the 'src' package) is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.indexer import build_index
from src.search import and_query, print_term, search_query


def build_small_index():
    """
    Helper to build a tiny index for search tests.
    """
    pages = [
        {
            "page_id": 0,
            "url": "http://example.com/0",
            "text": "good good friend",
        },
        {
            "page_id": 1,
            "url": "http://example.com/1",
            "text": "good enemy",
        },
        {
            "page_id": 2,
            "url": "http://example.com/2",
            "text": "neutral observer",
        },
    ]
    return build_index(pages)


def test_and_query_single_term():
    index_data = build_small_index()
    docs = and_query(index_data, ["good"])

    # Docs 0 and 1 contain 'good'
    assert docs == {0, 1}


def test_and_query_multiple_terms():
    index_data = build_small_index()
    docs = and_query(index_data, ["good", "friend"])

    # Only doc 0 contains both 'good' and 'friend'
    assert docs == {0}


def test_and_query_empty_terms_returns_empty_set():
    index_data = build_small_index()
    docs = and_query(index_data, [])

    assert docs == set()


def test_search_query_ranks_more_relevant_document_higher():
    """
    'good' appears twice in doc 0 and once in doc 1, so for
    query ['good'] we expect doc 0 to have a higher TF-IDF score.
    """
    index_data = build_small_index()
    results = search_query(index_data, ["good"])

    # results is a list of (doc_id, score) sorted by descending score
    assert len(results) == 2
    top_doc_id, top_score = results[0]
    second_doc_id, second_score = results[1]

    assert top_doc_id == 0
    assert second_doc_id == 1
    assert top_score > second_score


def test_print_term_existing_term():
    index_data = build_small_index()
    output = print_term(index_data, "good")

    # Should mention the term and its document frequency
    assert "Term: 'good'" in output
    assert "Document frequency: 2" in output
    # Should reference both doc_ids 0 and 1
    assert "doc_id=0" in output
    assert "doc_id=1" in output


def test_print_term_non_existent_term():
    index_data = build_small_index()
    output = print_term(index_data, "nonexistentterm")

    assert "No entries for term 'nonexistentterm'." in output