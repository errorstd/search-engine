"""
indexer.py

Builds and stores an inverted index from crawled pages.

The index structure (in-memory) is a dict with:
- "index": term -> list of postings
- "doc_id_to_url": doc_id (int) -> URL (str)
- "doc_lengths": doc_id (int) -> total token count (int)
- "doc_freq": term -> document frequency (int)
- "num_docs": total number of documents (int)

A posting is a dict:
- {"doc_id": int, "freq": int, "positions": list[int]}

The index is saved as JSON to data/index.json by default.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List

WORD_PATTERN = re.compile(r"[a-zA-Z]+")

DEFAULT_INDEX_PATH = os.path.join("data", "index.json")


def tokenize(text: str) -> List[str]:
    """
    Tokenise text into lowercase alphabetic words.

    Non-alphabetic characters are treated as delimiters.
    """
    return [match.group(0).lower() for match in WORD_PATTERN.finditer(text)]


def build_index(pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build an inverted index from a list of pages.

    Each page dict must have keys: "page_id", "url", "text".
    """
    # Temporary structure: term -> doc_id -> list of positions
    tmp_index: Dict[str, Dict[int, List[int]]] = {}
    doc_id_to_url: Dict[int, str] = {}
    doc_lengths: Dict[int, int] = {}

    for page in pages:
        doc_id = int(page["page_id"])
        url = str(page["url"])
        text = str(page["text"])

        tokens = tokenize(text)

        doc_id_to_url[doc_id] = url
        doc_lengths[doc_id] = len(tokens)

        for pos, term in enumerate(tokens):
            if term not in tmp_index:
                tmp_index[term] = {}
            if doc_id not in tmp_index[term]:
                tmp_index[term][doc_id] = []
            tmp_index[term][doc_id].append(pos)

    inv_index: Dict[str, List[Dict[str, Any]]] = {}
    doc_freq: Dict[str, int] = {}

    for term, postings_dict in tmp_index.items():
        postings: List[Dict[str, Any]] = []
        for doc_id, positions in postings_dict.items():
            postings.append(
                {
                    "doc_id": doc_id,
                    "freq": len(positions),
                    "positions": positions,
                }
            )
        inv_index[term] = postings
        doc_freq[term] = len(postings)

    index_data: Dict[str, Any] = {
        "index": inv_index,
        "doc_id_to_url": doc_id_to_url,
        "doc_lengths": doc_lengths,
        "doc_freq": doc_freq,
        "num_docs": len(doc_id_to_url),
    }
    return index_data


def save_index(index_data: Dict[str, Any], path: str = DEFAULT_INDEX_PATH) -> None:
    """
    Save index_data to JSON.

    JSON requires string keys, so we convert integer doc_ids to strings
    when saving and back to ints when loading.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    serialisable = {
        "index": index_data["index"],
        "doc_id_to_url": {str(k): v for k, v in index_data["doc_id_to_url"].items()},
        "doc_lengths": {str(k): v for k, v in index_data["doc_lengths"].items()},
        "doc_freq": index_data["doc_freq"],
        "num_docs": index_data["num_docs"],
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(serialisable, f, ensure_ascii=False, indent=2)


def load_index(path: str = DEFAULT_INDEX_PATH) -> Dict[str, Any]:
    """
    Load index_data from JSON and convert doc_ids back to integers.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Index file not found at '{path}'")

    with open(path, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    inv_index: Dict[str, List[Dict[str, Any]]] = loaded["index"]

    doc_id_to_url = {int(k): v for k, v in loaded["doc_id_to_url"].items()}
    doc_lengths = {int(k): v for k, v in loaded["doc_lengths"].items()}
    doc_freq = loaded["doc_freq"]
    num_docs = int(loaded["num_docs"])

    index_data: Dict[str, Any] = {
        "index": inv_index,
        "doc_id_to_url": doc_id_to_url,
        "doc_lengths": doc_lengths,
        "doc_freq": doc_freq,
        "num_docs": num_docs,
    }
    return index_data