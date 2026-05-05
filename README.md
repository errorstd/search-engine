# Search Engine Tool 

This project is a command-line search engine tool built for the COMP3011 *Web Services and Web Data* module at the University of Leeds.

It crawls the educational website [https://quotes.toscrape.com/](https://quotes.toscrape.com/), builds an inverted index of all words, and supports ranked search over the collected pages.

The implementation demonstrates web crawling, inverted index construction, and query processing, including an advanced TF‑IDF ranking feature beyond the core coursework requirements.[file:1]

---

## Features

- Crawl all quote pages from `https://quotes.toscrape.com/` following “Next” pagination.
- Respect a politeness window of at least **6 seconds** between successive HTTP requests.
- Build an **inverted index** storing, for each term:
  - Document IDs where it appears.
  - Term frequency within each document.
  - Positions of each occurrence within the document text.
- Case‑insensitive processing (e.g. `Good` and `good` are treated as the same term).
- Command‑line interface (CLI) with four commands:
  - `build` – crawl site and build index.
  - `load` – load the compiled index from disk.
  - `print <word>` – display postings for a specific term.
  - `find <terms...>` – Boolean AND query with TF‑IDF ranking.
- Robust handling of edge cases:
  - Empty queries (`find` with no terms).
  - Non‑existent terms.
  - Commands used before the index is loaded.
- Automated test suite with `pytest` and coverage reporting.
- Clear project structure compatible with the coursework brief.

---

## Project Structure

```text
search-engine/
  src/
    __init__.py
    crawler.py     # Crawls quotes.toscrape.com and extracts text
    indexer.py     # Builds and saves/loads the inverted index
    search.py      # Query processing and TF-IDF ranking
    main.py        # CLI shell (build, load, print, find)
  tests/
    test_crawler.py
    test_indexer.py
    test_search.py
  data/
    index.json     # Compiled index file (created by `build`)
  requirements.txt
  README.md
```

---

## Installation and Setup

### Prerequisites

- Python 3.10+ (tested with Python 3.14 on Windows).
- Git (optional but recommended).

### 1. Clone the repository

```bash
git clone <YOUR_REPO_URL> search-engine
cd search-engine
```

Replace `<YOUR_REPO_URL>` with your actual GitHub repository URL.

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Main dependencies:

- `requests` – HTTP client for web crawling.
- `beautifulsoup4` – HTML parsing.
- `pytest`, `pytest-cov` – testing and coverage.

---

## Usage

All commands are provided via a simple REPL (read–eval–print loop) implemented in `src/main.py`.

From the project root (with the virtual environment activated):

```bash
python -m src.main
```

You should see:

```text
Simple Search Tool
Commands: build, load, print <word>, find <terms...>, quit/exit
>
```

### 1. `build` – crawl website and build index

```text
> build
[build] Crawling website...
[build] Crawled N pages. Building index...
[build] Index built with N documents and M unique terms.
[build] Index saved to disk.
```

- Crawls `https://quotes.toscrape.com/`, following “Next” links until no more pages.
- Enforces a **6 second delay** between successive HTTP requests.
- Builds the inverted index and writes it to `data/index.json`.

> Note: `build` can take a little time due to the politeness window.

### 2. `load` – load compiled index

```text
> load
[load] Loading index from disk...
[load] Loaded index with N documents and M unique terms.
```

- Loads `data/index.json` into memory.
- Must be run before using `print` or `find` after starting the tool.

If the index file does not exist yet, you will see an error message and should run `build` first.

### 3. `print <word>` – show postings for a term

```text
> print good
Term: 'good'
Document frequency: 2
- doc_id=0, freq=2, positions=[1]
- doc_id=1, freq=1, positions=
```

- Normalises the term to lowercase.
- Prints:
  - Document frequency (how many documents contain the term).
  - For each document:
    - `doc_id`
    - `freq` (term frequency in that document)
    - `positions` (token positions within the document).

If the term is not found:

```text
> print nonsenseword
No entries for term 'nonsenseword'.
```

### 4. `find <terms...>` – AND query with TF‑IDF ranking

```text
> find good friends
[find] Found 1 matching document(s).
1. doc_id=0, score=0.6931, url=http://example.com/0
```

- Normalises all query terms to lowercase.
- Uses **Boolean AND** semantics:
  - A document must contain **all** query terms to match.
- Uses a simple **TF‑IDF score**:
  - Term frequency: \( \text{tf}(t, d) = 1 + \log(\text{freq}(t, d)) \)
  - Inverse document frequency: \( \text{idf}(t) = \log(N / \text{df}(t)) \)
  - Score per document: \( \sum_{t \in \text{query}} \text{tf}(t, d) \cdot \text{idf}(t) \)
- Results are printed sorted by descending score, including `doc_id`, score, and URL.

Edge cases:

- Empty query:

  ```text
  > find
  [find] Please provide at least one search term, e.g. 'find good friends'.
  ```

- Query with no matching documents:

  ```text
  > find totallymadeupword
  [find] No matching documents found.
  ```

### 5. Exiting

```text
> quit
Goodbye.
```

or

```text
> exit
Goodbye.
```

---

## Testing

The project includes a test suite using `pytest`:

- `tests/test_crawler.py`
  - Tests HTML parsing helpers (text extraction and pagination link detection) without performing real HTTP requests.
- `tests/test_indexer.py`
  - Tests tokenisation, inverted index construction, term frequencies, and positions.
- `tests/test_search.py`
  - Tests AND query logic, TF‑IDF ranking, and `print` behaviour (including non‑existent terms).

### Running the tests

From the project root with the virtual environment activated:

```bash
pytest
```

### Running tests with coverage

```bash
pytest --cov=src --cov-report=term-missing
```

This prints a coverage summary for the `src` package, which you can show in your video when discussing test coverage and testing strategy.[file:1]

---

## Design Overview

### Crawler (`src/crawler.py`)

- Uses `requests` to fetch pages and `BeautifulSoup` to parse the HTML.
- Extracts:
  - Quote text (`.quote .text`)
  - Authors (`.quote .author`)
  - Tags (`.quote .tags .tag`)
- Follows the “Next” pagination link (`li.next a`) until there are no more pages.
- Respects a **configurable politeness delay** between successive requests (default 6 seconds).[file:1]

### Indexer (`src/indexer.py`)

- Tokenises text into alphabetic words using a regular expression, converting to lowercase.
- Builds an inverted index:

  ```python
  index: Dict[str, List[Posting]]
  Posting = {"doc_id": int, "freq": int, "positions": List[int]}
  ```

- Tracks:
  - `doc_id_to_url`: mapping from internal document ID to URL.
  - `doc_lengths`: total tokens per document.
  - `doc_freq`: document frequency per term.
  - `num_docs`: total number of documents.
- Saves/loads the index as JSON (`data/index.json`) for reproducibility.

### Search (`src/search.py`)

- Boolean AND query over the inverted index to identify candidate documents.
- Computes TF‑IDF scores to rank results by relevance.
- Provides human‑readable output for the `print` command.

### CLI Shell (`src/main.py`)

- Implements a simple REPL with commands:
  - `build`, `load`, `print <word>`, `find <terms...>`, `quit`, `exit`.
- Ensures index is loaded before search/print operations.
- Provides clear messages for incorrect usage and edge cases.

---

## Coursework Notes

This project is designed to meet the COMP3011 Coursework 2 requirements:

- Crawling implementation (politeness window, pagination, basic error handling).[file:1]
- Inverted index with word statistics (frequency and positions per page).[file:1]
- Storage and retrieval via `build`/`load` commands using a compiled index file.
- Search functionality via `print` and `find` for single and multi‑word queries.
- Automated tests and coverage reporting.
- Clear repository structure and documentation consistent with the assessment brief.[file:1]

---

## GenAI Usage (Declaration)


This project was developed with occasional assistance from GenAI tools (e.g. NotebookLLM Perplexity) for:

- Brainstorming data structures and TF‑IDF formulas.
- Generating initial test ideas and boilerplate code.
- Refining documentation and README wording.

All AI‑suggested code was reviewed, adapted, and tested to ensure correctness and understanding.  
In the accompanying video demonstration, I discuss specific examples of where GenAI helped, where suggestions needed correction, and how using AI affected my learning experience.