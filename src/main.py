"""
main.py

Command-line shell for the search tool.

Supported commands:
- build            : crawl website, build index, and save to disk
- load             : load existing index from disk
- print <word>     : print postings for a given word
- find <terms...>  : AND-query search with TF-IDF ranking

Example usage:

> build
> load
> print nonsense
> find good friends
"""

from __future__ import annotations

from typing import Any, Dict, List

from .crawler import crawl_website
from .indexer import build_index, load_index, save_index
from .search import print_term, search_query

def handle_build() -> None:
    """
    Crawl the website and build the inverted index, then save it to disk.
    """
    print("[build] Crawling website...")
    pages = crawl_website()
    print(f"[build] Crawled {len(pages)} pages. Building index...")

    index_data = build_index(pages)
    save_index(index_data)

    print(
        f"[build] Index built with {index_data['num_docs']} documents "
        f"and {len(index_data['index'])} unique terms."
    )
    print("[build] Index saved to disk.")


def handle_load() -> Dict[str, Any]:
    """
    Load index from disk and return it.
    """
    print("[load] Loading index from disk...")
    index_data = load_index()
    print(
        f"[load] Loaded index with {index_data['num_docs']} documents "
        f"and {len(index_data['index'])} unique terms."
    )
    return index_data


def handle_print(index_data: Dict[str, Any], args: List[str]) -> None:
    """
    Handle the 'print' command.
    """
    if not args:
        print("[print] Usage: print <word>")
        return

    term = args[0]
    output = print_term(index_data, term)
    print(output)


def handle_find(index_data: Dict[str, Any], args: List[str]) -> None:
    """
    Handle the 'find' command (multi-word AND query with ranking).
    """
    if not args:
        print("[find] Please provide at least one search term, e.g. 'find good friends'.")
        return

    results = search_query(index_data, args)
    if not results:
        print("[find] No matching documents found.")
        return

    print(f"[find] Found {len(results)} matching document(s).")
    for rank, (doc_id, score) in enumerate(results, start=1):
        url = index_data["doc_id_to_url"].get(doc_id, "<unknown>")
        print(f"{rank}. doc_id={doc_id}, score={score:.4f}, url={url}")


def repl() -> None:
    """
    Simple read-eval-print loop (REPL) for the search tool.
    """
    index_data: Dict[str, Any] | None = None

    print("Simple Search Tool")
    print("Commands: build, load, print <word>, find <terms...>, quit/exit")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not line:
            continue

        parts = line.split()
        command = parts[0].lower()
        args = parts[1:]

        if command in ("quit", "exit"):
            print("Goodbye.")
            break

        if command == "build":
            handle_build()
            # Reset in-memory index; user should run 'load' afterwards.
            index_data = None
        elif command == "load":
            try:
                index_data = handle_load()
            except FileNotFoundError as exc:
                print(f"[load] {exc}")
                index_data = None
        elif command == "print":
            if index_data is None:
                print("[print] Please run 'load' first to load the index.")
            else:
                handle_print(index_data, args)
        elif command == "find":
            if index_data is None:
                print("[find] Please run 'load' first to load the index.")
            else:
                handle_find(index_data, args)
        else:
            print("Unknown command. Available commands: build, load, print, find, quit, exit.")


if __name__ == "__main__":
    repl()