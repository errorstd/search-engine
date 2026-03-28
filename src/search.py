"""
search.py

Implements search operations over an inverted index:
- print_term: show postings for a given term
- search_query: AND query with TF-IDF ranking for results

The index_data structure must match indexer.build_index().
"""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Set, Tuple


def get_postings(index_data: Dict[str, Any], term: str) -> List[Dict[str, Any]]:
    """
    Get postings list for a normalised term.
    """
    return index_data["index"].get(term, [])


def docs_for_term(index_data: Dict[str, Any], term: str) -> Set[int]:
    """
    Return the set of document IDs that contain the term.
    """
    return {posting["doc_id"] for posting in get_postings(index_data, term)}


def and_query(index_data: Dict[str, Any], terms: Iterable[str]) -> Set[int]:
    """
    Perform a simple AND query: return doc_ids that contain all terms.
    """
    normalised_terms = [t.lower() for t in terms if t.strip()]
    if not normalised_terms:
        return set()

    doc_sets: List[Set[int]] = [docs_for_term(index_data, t) for t in normalised_terms]
    if not doc_sets:
        return set()

    result = doc_sets[0]
    for s in doc_sets[1:]:
        result = result & s
    return result


def compute_idf(index_data: Dict[str, Any], term: str) -> float:
    """
    Compute inverse document frequency for a term.

    idf(t) = log(N / (df(t) + 1))
    """
    num_docs = index_data["num_docs"]
    df = index_data["doc_freq"].get(term, 0)
    return math.log(num_docs / (df + 1)) if num_docs > 0 else 0.0


def score_document(index_data: Dict[str, Any], doc_id: int, terms: Iterable[str]) -> float:
    """
    Compute a simple TF-IDF score for a document given query terms.
    """
    score = 0.0
    normalised_terms = [t.lower() for t in terms if t.strip()]

    for term in normalised_terms:
        postings = get_postings(index_data, term)
        posting = next((p for p in postings if p["doc_id"] == doc_id), None)
        if posting is None:
            continue

        freq = posting["freq"]
        if freq <= 0:
            continue

        tf = 1.0 + math.log(freq)
        idf = compute_idf(index_data, term)
        score += tf * idf

    return score


def search_query(index_data: Dict[str, Any], terms: List[str]) -> List[Tuple[int, float]]:
    """
    Execute an AND query and return a ranked list of (doc_id, score).

    Documents are ranked by descending TF-IDF score.
    """
    candidate_docs = and_query(index_data, terms)
    if not candidate_docs:
        return []

    scored: List[Tuple[int, float]] = []
    for doc_id in candidate_docs:
        s = score_document(index_data, doc_id, terms)
        scored.append((doc_id, s))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


def print_term(index_data: Dict[str, Any], term: str) -> str:
    """
    Build a human-readable string representing the postings for a term.

    This is used by the 'print' command in the CLI.
    """
    normalised = term.lower()
    postings = get_postings(index_data, normalised)

    if not postings:
        return f"No entries for term '{normalised}'."

    lines: List[str] = [f"Term: '{normalised}'", f"Document frequency: {len(postings)}"]
    for posting in postings:
        doc_id = posting["doc_id"]
        freq = posting["freq"]
        positions = posting["positions"]
        lines.append(
            f"- doc_id={doc_id}, freq={freq}, positions={positions}"
        )

    return "\n".join(lines)