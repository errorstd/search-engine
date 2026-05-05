"""
tests/test_indexer.py

Unit tests for indexer.py.
"""

from __future__ import annotations

import os
import sys

# Ensure the project root (containing the 'src' package) is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.indexer import build_index, tokenize


def test_tokenize_basic_text():
    text = "Good, bad!! And GOOD again."
    tokens = tokenize(text)

    # Only alphabetic, all lowercase
    assert tokens == ["good", "bad", "and", "good", "again"]


def test_build_index_structure_and_statistics():
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
    ]

    index_data = build_index(pages)

    # High-level stats
    assert index_data["num_docs"] == 2
    assert index_data["doc_id_to_url"][0] == "http://example.com/0"
    assert index_data["doc_id_to_url"][1] == "http://example.com/1"

    # Document lengths
    assert index_data["doc_lengths"][0] == 3  # good, good, friend
    assert index_data["doc_lengths"][1] == 2  # good, enemy

    inv_index = index_data["index"]
    doc_freq = index_data["doc_freq"]

    # Term 'good' appears in both docs
    good_postings = inv_index["good"]
    assert len(good_postings) == 2
    assert doc_freq["good"] == 2

    # Check frequencies and positions
    posting_doc0 = next(p for p in good_postings if p["doc_id"] == 0)
    posting_doc1 = next(p for p in good_postings if p["doc_id"] == 1)

    assert posting_doc0["freq"] == 2
    assert posting_doc0["positions"] == [0, 1]

    assert posting_doc1["freq"] == 1
    assert posting_doc1["positions"] == [0]

    # Term 'friend' appears only in doc 0
    friend_postings = inv_index["friend"]
    assert len(friend_postings) == 1
    assert doc_freq["friend"] == 1

    posting_friend_doc0 = friend_postings[0]
    assert posting_friend_doc0["doc_id"] == 0
    assert posting_friend_doc0["freq"] == 1
    assert posting_friend_doc0["positions"] == [2]