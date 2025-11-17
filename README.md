# rag-chunk

**Current Version: 0.2.0** 🎉

CLI tool to parse, chunk, and evaluate Markdown documents for Retrieval-Augmented Generation (RAG) pipelines with token-accurate chunking support.

Available on PyPI: https://pypi.org/project/rag-chunk/

## ✨ Features

- 📄 Parse and clean Markdown files
- ✂️ Multiple chunking strategies:
  - `fixed-size`: Split by fixed word/token count
  - `sliding-window`: Overlapping chunks for context preservation
  - `paragraph`: Natural paragraph boundaries
- 🎯 **Token-based chunking** with tiktoken (OpenAI models: GPT-3.5, GPT-4, etc.)
- 🎨 **Model selection** via `--tiktoken-model` flag
- 📊 Recall-based evaluation with test JSON files
- 🌈 Beautiful CLI output with Rich tables
- 📈 Compare all strategies with `--strategy all`
- 💾 Export results as JSON or CSV

### Demo
![rag-chunk demo](demo.gif)

## 🚀 Roadmap

`rag-chunk` is actively developed! Here's the plan to move from a useful tool to a full-featured chunking workbench.

### ✅ Version 0.1.0 – Launched
* [x] Core CLI engine (`argparse`)
* [x] Markdown (`.md`) file parsing
* [x] Basic chunking strategies: `fixed-size`, `sliding-window`, and `paragraph` (word-based)
* [x] Evaluation harness: calculate **Recall score** from a `test-file.json`
* [x] Beautiful CLI output (`rich` tables)
* [x] Published on PyPI: `pip install rag-chunk`

### ✅ Version 0.2.0 – Completed
* [x] **Tiktoken Support:** Added `--use-tiktoken` flag for precise token-based chunking
* [x] **Model Selection:** Added `--tiktoken-model` to choose tokenization model (default: `gpt-3.5-turbo`)
* [x] **Improved Documentation:** Updated README with tiktoken usage examples and comparisons
* [x] **Enhanced Testing:** Added comprehensive unit tests for token-based chunking
* [x] **Optional Dependencies:** tiktoken available via `pip install rag-chunk[tiktoken]`

### 🎯 Version 0.3.0 – Planned
* [ ] **Recursive Character Splitting:** Add LangChain's `RecursiveCharacterTextSplitter` for semantic chunking
  - Install with: `pip install rag-chunk[langchain]`
  - Strategy: `--strategy recursive-character`
  - Works with both word-based and tiktoken modes
* [ ] **More File Formats:** Support `.txt`, `.rst`, and other plain text formats
* [ ] **Additional Metrics:** Add precision, F1-score, and chunk quality metrics

### 📈 Version 1.0.0 – Future
* [ ] **Advanced Strategies:** Hierarchical chunking, semantic similarity-based splitting
* [ ] **Export Connectors:** Direct integration with vector stores (Pinecone, Weaviate, Chroma)
* [ ] **Benchmarking Mode:** Automated strategy comparison with recommendations
* [ ] **MLFlow Integration:** Track experiments and chunking configurations
* [ ] **Performance Optimization:** Parallel processing for large document sets


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
pip install rag-chunk
```

For token-based chunking with tiktoken support:

```bash
pip install rag-chunk[tiktoken]
```

Or install from source:

```bash
pip install .
```

Development mode:

```bash
pip install -e .
pip install -e .[tiktoken]  # with tiktoken support
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
| `--chunk-size` | Number of words or tokens per chunk | `200` |
| `--overlap` | Number of overlapping words or tokens (for sliding-window) | `50` |
| `--use-tiktoken` | Use tiktoken for precise token-based chunking (requires `pip install rag-chunk[tiktoken]`) | `False` |
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

## Using Tiktoken for Precise Token-Based Chunking

By default, `rag-chunk` uses word-based tokenization (whitespace splitting). For precise token-level chunking that matches LLM context limits (e.g., GPT-3.5/GPT-4), use the `--use-tiktoken` flag.

### Installation

```bash
pip install rag-chunk[tiktoken]
```

### Usage Examples

**Token-based fixed-size chunking:**

```bash
rag-chunk analyze examples/ --strategy fixed-size --chunk-size 512 --use-tiktoken --output table
```

This creates chunks of exactly 512 tokens (as counted by tiktoken for GPT models), not 512 words.

**Compare word-based vs token-based chunking:**

```bash
# Word-based (default)
rag-chunk analyze examples/ --strategy fixed-size --chunk-size 200 --output json

# Token-based
rag-chunk analyze examples/ --strategy fixed-size --chunk-size 200 --use-tiktoken --output json
```

**Token-based with sliding window:**

```bash
rag-chunk analyze examples/ --strategy sliding-window --chunk-size 1024 --overlap 128 --use-tiktoken --test-file examples/questions.json --top-k 3
```

### When to Use Tiktoken

- ✅ **Use tiktoken when:**
  - Preparing chunks for OpenAI models (GPT-3.5, GPT-4)
  - You need to respect strict token limits (e.g., 8k, 16k context windows)
  - Comparing chunking strategies with token-accurate measurements
  - Your documents contain special characters, emojis, or non-ASCII text

- ⚠️ **Use word-based (default) when:**
  - Quick prototyping and testing
  - Working with well-formatted English text
  - Don't need exact token counts
  - Want to avoid the tiktoken dependency

### Token Counting

You can also use tiktoken in your own scripts:

```python
from src.chunker import count_tokens

text = "Your document text here..."

# Word-based count
word_count = count_tokens(text, use_tiktoken=False)
print(f"Words: {word_count}")

# Token-based count (requires tiktoken installed)
token_count = count_tokens(text, use_tiktoken=True)
print(f"Tokens: {token_count}")
```

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

## Note on Tokenization

By default, `--chunk-size` and `--overlap` count **words** (whitespace-based tokenization). This keeps the tool simple and dependency-free.

For precise token-level chunking that matches LLM token counts (e.g., OpenAI GPT models using subword tokenization), use the `--use-tiktoken` flag after installing the optional dependency:

```bash
pip install rag-chunk[tiktoken]
rag-chunk analyze docs/ --strategy fixed-size --chunk-size 512 --use-tiktoken
```

See the [Using Tiktoken](#using-tiktoken-for-precise-token-based-chunking) section for more details.
