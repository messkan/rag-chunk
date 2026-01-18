# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2026-01-18

### Added
- **Header-Aware Chunking Strategy** (`--strategy header`)
  - Split text by markdown headers (#, ##, ###, ####) while respecting chunk size limits
  - Preserves document structure with metadata about headers and hierarchy
  - Automatically splits large sections using sliding window when they exceed chunk size
  - Ideal for technical documentation and structured markdown files

- **Semantic Chunking Strategy** (`--strategy semantic`)
  - Uses sentence embeddings to split at semantic boundaries
  - Groups consecutive sentences with high semantic similarity
  - Splits when similarity drops below threshold or chunk size is reached
  - Powered by sentence-transformers (all-MiniLM-L6-v2 model)
  - Requires `pip install rag-chunk[semantic]`

- **Embedding-Based Retrieval** (`--use-embeddings`)
  - Semantic similarity matching using cosine similarity on sentence embeddings
  - Superior to lexical matching for conceptual/semantic queries
  - Works with all chunking strategies
  - Uses cached embedding model for efficiency

- **GitHub Pages Documentation**
  - Beautiful HTML documentation site
  - Comprehensive feature explanations and usage examples
  - Interactive design with gradient backgrounds and hover effects
  - Strategy comparison table and CLI reference

### Changed
- Updated version from 0.3.0 to 0.4.0
- Enhanced README with new features, installation options, and examples
- Added `semantic` optional dependency group in pyproject.toml
- Updated CLI strategy choices to include `header` and `semantic`
- Modified `scorer.evaluate_strategy()` to accept `use_embeddings` parameter
- Enhanced `scorer.retrieve_top_k()` to support both lexical and semantic retrieval

### Technical Details
- `chunker.header_aware_chunks()`: Splits by markdown headers with regex pattern matching
- `chunker.semantic_chunks()`: Uses sentence-transformers for embedding-based splitting
- `scorer.semantic_similarity()`: Computes cosine similarity between embeddings
- `scorer.get_embedding_model()`: Global model cache to avoid reloading
- New dependencies: `sentence-transformers>=2.2.0`, `numpy>=1.24.0`

## [0.3.0] - 2025-11-25

### Added
- **Recursive Character Splitting**: New strategy `recursive-character` using LangChain (requires `rag-chunk[langchain]`).
- **New File Formats**: Support for parsing `.txt` files in addition to Markdown.
- **Advanced Metrics**: Added Precision and F1-score to evaluation reports.

