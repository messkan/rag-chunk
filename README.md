# rag-chunk

CLI tool to parse, chunk, and evaluate Markdown documents for Retrieval-Augmented Generation (RAG) preparation.
## 🎉 First Public Release

Available on PyPI: https://pypi.org/project/rag-chunk/

### Features
- ✅ Parse and clean Markdown files
- ✅ Three chunking strategies: fixed-size, sliding-window, paragraph
- ✅ Recall-based evaluation with test JSON files
- ✅ CLI with table/JSON/CSV output formats
- ✅ Realistic example corpus included

### Demo
![rag-chunk demo](demo.gif)

## 🚀 Roadmap

`rag-chunk` is actively developed! Here's the plan to move from a basic tool to a full-featured chunking workbench.

### ✅ Version 0.1 – Launched
* [x] Core CLI engine (`click`)
* [x] Markdown (`.md`) file parsing (`mistune`)
* [x] Basic chunking strategies: `fixed-size` and `paragraph` (word-based)
* [x] Evaluation harness: calculate **Recall score** from a `test-file.json`
* [x] **PyPI Publication:** Installable via `pip install rag-chunk`

### 🎯 Version 0.2 – In Progress
* [x] CLI output formatting (`rich` tables)
* [x] **Demo GIF:** Showcase the tool in action in the README
* [ ] **`tiktoken` Support:** Add `--use-tiktoken` flag for precise, token-based chunking
* [ ] CLI/UX improvements and bug fixes

### 📈 Version 1.0 – Planned
* [ ] **More Strategies:** Add advanced strategies like `RecursiveCharacterTextSplitter`, `HierarchicalChunker`
* [ ] **More File Types:** Support `.txt`, `.rst`, and other plain text formats
* [ ] **Export & Logging:** Save results as JSON/CSV, optional MLFlow integration
* [ ] **Benchmarking Mode:** Compare chunking strategies automatically


### Installation
```bash
pip install rag-chunk
## Features

- Parse and clean Markdown files in a folder
- Chunk text using fixed-size, sliding-window, or paragraph-based strategies
- Evaluate chunk recall based on a provided test JSON file
- Output results as table, JSON, or CSV
- Store generated chunks temporarily in `.chunks`

## Installation

```bash
pip install .
```

or in development mode:

```bash
pip install -e .
```

## Quick Start

```bash
rag-chunk analyze examples/ --strategy all --chunk-size 150 --overlap 30 --test-file examples/questions.json --top-k 3 --output table
```

## CLI Usage

```bash
rag-chunk analyze <folder> [options]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--strategy` | Chunking strategy: `fixed-size`, `sliding-window`, `paragraph`, or `all` | `fixed-size` |
| `--chunk-size` | Number of words per chunk | `200` |
| `--overlap` | Number of overlapping words (for sliding-window) | `50` |
| `--test-file` | Path to JSON test file with questions | None |
| `--top-k` | Number of chunks to retrieve per question | `3` |
| `--output` | Output format: `table`, `json`, or `csv` | `table` |

If `--strategy all` is chosen, every strategy is run with the supplied chunk-size and overlap where applicable.

## Examples

### Basic Usage: Generate Chunks Only

Analyze markdown files and generate chunks without evaluation:

```bash
rag-chunk analyze examples/ --strategy paragraph
```

**Output:**
```
strategy  | chunks | avg_recall | saved                            
----------+--------+------------+----------------------------------
paragraph | 12     | 0.0        | .chunks/paragraph-20251115-020145
Total text length (chars): 3542
```

### Compare All Strategies

Run all chunking strategies with custom parameters:

```bash
rag-chunk analyze examples/ --strategy all --chunk-size 100 --overlap 20 --output table
```

**Output:**
```
strategy       | chunks | avg_recall | saved                                 
---------------+--------+------------+---------------------------------------
fixed-size     | 36     | 0.0        | .chunks/fixed-size-20251115-020156    
sliding-window | 45     | 0.0        | .chunks/sliding-window-20251115-020156
paragraph      | 12     | 0.0        | .chunks/paragraph-20251115-020156
Total text length (chars): 3542
```

### Evaluate with Test File

Measure recall using a test file with questions and relevant phrases:

```bash
rag-chunk analyze examples/ --strategy all --chunk-size 150 --overlap 30 --test-file examples/questions.json --top-k 3 --output table
```

**Output:**
```
strategy       | chunks | avg_recall | saved                                 
---------------+--------+------------+---------------------------------------
fixed-size     | 24     | 0.7812     | .chunks/fixed-size-20251115-020203    
sliding-window | 32     | 0.8542     | .chunks/sliding-window-20251115-020203
paragraph      | 12     | 0.9167     | .chunks/paragraph-20251115-020203
```

Paragraph-based chunking achieves highest recall (91.67%) because it preserves semantic boundaries in well-structured documents.

### Export Results as JSON

```bash
rag-chunk analyze examples/ --strategy sliding-window --chunk-size 120 --overlap 40 --test-file examples/questions.json --top-k 5 --output json > results.json
```

**Output structure:**
```json
{
  "results": [
    {
      "strategy": "sliding-window",
      "chunks": 38,
      "avg_recall": 0.8958,
      "saved": ".chunks/sliding-window-20251115-020210"
    }
  ],
  "detail": {
    "sliding-window": [
      {
        "question": "What are the three main stages of a RAG pipeline?",
        "recall": 1.0
      },
      {
        "question": "What is the main advantage of RAG over pure generative models?",
        "recall": 0.6667
      }
    ]
  }
}
```

### Export as CSV

```bash
rag-chunk analyze examples/ --strategy all --test-file examples/questions.json --output csv
```

Creates `analysis_results.csv` with columns: strategy, chunks, avg_recall, saved.

## Test File Format

JSON file with a `questions` array (or direct array at top level):

```json
{
  "questions": [
    {
      "question": "What are the three main stages of a RAG pipeline?",
      "relevant": ["indexing", "retrieval", "generation"]
    },
    {
      "question": "What is the main advantage of RAG over pure generative models?",
      "relevant": ["grounding", "retrieved documents", "hallucinate"]
    }
  ]
}
```

- `question`: The query text used for chunk retrieval
- `relevant`: List of phrases/terms that should appear in relevant chunks

**Recall calculation:** For each question, the tool retrieves top-k chunks using lexical similarity and checks how many `relevant` phrases appear in those chunks. Recall = (found phrases) / (total relevant phrases). Average recall is computed across all questions.

## Understanding the Output

### Chunks
Number of chunks created by the strategy. More chunks = finer granularity but higher indexing cost.

### Average Recall
Percentage of relevant phrases successfully retrieved in top-k chunks (0.0 to 1.0). Higher is better.

**Interpreting recall:**
- **> 0.85**: Excellent - strategy preserves most relevant information
- **0.70 - 0.85**: Good - acceptable for most use cases
- **0.50 - 0.70**: Fair - consider adjusting chunk size or strategy
- **< 0.50**: Poor - important information being lost or fragmented

### Saved Location
Directory where chunks are written as individual `.txt` files for inspection.

## Choosing the Right Strategy

| Strategy | Best For | Chunk Size Recommendation |
|----------|----------|---------------------------|
| **fixed-size** | Uniform processing, consistent latency | 150-250 words |
| **sliding-window** | Preserving context at boundaries, dense text | 120-200 words, 20-30% overlap |
| **paragraph** | Well-structured docs with clear sections | N/A (variable) |

**General guidelines:**
1. Start with **paragraph** for markdown with clear structure
2. Use **sliding-window** if paragraphs are too long (>300 words)
3. Use **fixed-size** as baseline for comparison
4. Always test with representative questions from your domain

## Extending

Add a new chunking strategy:

1. Implement a function in `src/chunker.py`:
```python
def my_custom_chunks(text: str, chunk_size: int, overlap: int) -> List[Dict]:
    chunks = []
    # Your logic here
    chunks.append({"id": 0, "text": "chunk text"})
    return chunks
```

2. Register in `STRATEGIES`:
```python
STRATEGIES = {
    "custom": lambda text, chunk_size=200, overlap=0: my_custom_chunks(text, chunk_size, overlap),
    ...
}
```

3. Use via CLI:
```bash
rag-chunk analyze docs/ --strategy custom --chunk-size 180
```

## Project Structure

```
rag-chunk/
├── src/
│   ├── __init__.py
│   ├── parser.py       # Markdown parsing and cleaning
│   ├── chunker.py      # Chunking strategies
│   ├── scorer.py       # Retrieval and recall evaluation
│   └── cli.py          # Command-line interface
├── tests/
│   └── test_basic.py   # Unit tests
├── examples/
│   ├── rag_introduction.md
│   ├── chunking_strategies.md
│   ├── evaluation_metrics.md
│   └── questions.json
├── .chunks/            # Generated chunks (gitignored)
├── pyproject.toml
├── README.md
└── .gitignore
```

## License

MIT

## Note on tokenization

Currently the `--chunk-size` and `--overlap` options count **words** (whitespace-based tokenization). This keeps the tool simple and dependency-free, but it does not match the token counts used by LLMs (for example, OpenAI GPT models use subword tokenization).

We will soon add optional support for `tiktoken` to enable precise token-level chunking that matches model context limits. When available you will be able to enable it via a CLI flag (for example `--use-tiktoken`) or install the optional dependency `rag-chunk[tiktoken]`.

In the meantime, treat `--chunk-size` and `--overlap` as word-based estimates and tune them using your test questions to find the right granularity.
